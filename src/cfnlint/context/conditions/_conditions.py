"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterator, TypeGuard

from sympy import Not, Or, Symbol
from sympy.assumptions.cnf import EncodedCNF
from sympy.logic.inference import satisfiable

from cfnlint.conditions._utils import add_equivalence, get_hash
from cfnlint.context.conditions._condition import Condition
from cfnlint.context.conditions._equals import Equal
from cfnlint.context.conditions._utils import (
    build_instance_from_scenario,
    get_conditions_from_property,
)
from cfnlint.context.conditions.exceptions import Unsatisfiable
from cfnlint.helpers import is_function

if TYPE_CHECKING:
    from cfnlint.context.context import Context, Parameter


def _ref_name(instance: Any) -> str | None:
    fn_k, fn_v = is_function(instance)
    if fn_k == "Ref" and isinstance(fn_v, str):
        return fn_v
    return None


def _is_literal_map(instance: Any) -> TypeGuard[dict[str, Any]]:
    # A key the YAML decoder kept as a non-string (an unquoted account ID)
    # could be the one a Ref resolves to, so such a map is not read.
    return (
        isinstance(instance, dict)
        and "Fn::Transform" not in instance
        and all(isinstance(k, str) for k in instance)
    )


def _find_in_map_true_values(
    fn_v: Any, mappings: dict[str, Any], value: str
) -> tuple[str, frozenset[str]] | None:
    """For a Fn::FindInMap with one key a Ref and the other keys static,
    return the hash of the Ref and the Ref values whose lookup returns
    ``value``.  A Ref value with no entry is left out, because the lookup
    fails for it.  Returns None when the mapping cannot be read as written."""
    if "Fn::Transform" in mappings:
        return None
    if not isinstance(fn_v, list) or len(fn_v) != 3:
        return None
    map_name, top_key, second_key = fn_v
    if not isinstance(map_name, str):
        return None
    mapping = mappings.get(map_name)
    if not _is_literal_map(mapping):
        return None

    if (ref := _ref_name(top_key)) is not None and isinstance(second_key, str):
        if not all(_is_literal_map(entry) for entry in mapping.values()):
            return None
        lookups = {
            k: entry[second_key] for k, entry in mapping.items() if second_key in entry
        }
    elif (ref := _ref_name(second_key)) is not None and isinstance(top_key, str):
        entry = mapping.get(top_key)
        if not _is_literal_map(entry):
            return None
        lookups = entry
    else:
        return None

    if not all(isinstance(v, str) for v in lookups.values()):
        return None

    return get_hash({"Ref": ref}), frozenset(
        k for k, v in lookups.items() if v == value
    )


def _true_values(
    equal: Equal, mappings: dict[str, Any]
) -> list[tuple[str, frozenset[str]]]:
    """Return, for each expression an Fn::Equals compares to a string, the
    hash of the expression and the values of it that make the Fn::Equals
    true.  A Fn::FindInMap keyed by a Ref also yields the Ref."""
    if not isinstance(equal.left.instance, str):
        return []
    if not isinstance(equal.right.instance, dict):
        return []
    results = [(equal.right.hash, frozenset([equal.left.instance]))]
    fn_k, fn_v = is_function(equal.right.instance)
    # equal.instance[0] is the operand as written; left.instance is the
    # string form, which turns a YAML true into "True".
    if fn_k == "Fn::FindInMap" and isinstance(equal.instance[0], str):
        found = _find_in_map_true_values(fn_v, mappings, equal.left.instance)
        if found is not None:
            results.append(found)
    return results


def _allowed_values_by_ref(
    parameters: dict[str, "Parameter"],
) -> dict[str, frozenset[str]]:
    """Map the Ref hash of each parameter whose AllowedValues are all
    strings to those values."""
    result = {}
    for name, parameter in parameters.items():
        allowed = parameter.allowed_values
        if (
            isinstance(allowed, list)
            and allowed
            and all(isinstance(v, str) for v in allowed)
        ):
            result[get_hash({"Ref": name})] = frozenset(allowed)
    return result


# Up to this many symbols, at-most-one is written as one clause per pair.
_PAIRWISE_AT_MOST_ONE = 7


def _add_at_most_one(cnf: EncodedCNF, ref_hash: str, symbols: list[Any]) -> None:
    """Add clauses so that at most one of ``symbols`` is true."""
    if len(symbols) <= _PAIRWISE_AT_MOST_ONE:
        for a, b in itertools.combinations(symbols, 2):
            cnf.add_prop(Or(Not(a), Not(b)))
        return
    # Binary encoding: each symbol implies its own index in bit variables.
    bits = [
        Symbol(f"bit:{ref_hash}:{j}") for j in range((len(symbols) - 1).bit_length())
    ]
    for n, symbol in enumerate(symbols):
        for j, bit in enumerate(bits):
            cnf.add_prop(Or(Not(symbol), bit if (n >> j) & 1 else Not(bit)))


def _add_value_constraints(
    cnf: EncodedCNF,
    ref_hash: str,
    members: list[tuple[Symbol, frozenset[str]]],
    allowed: frozenset[str] | None,
) -> None:
    """Constrain the Fn::Equals that depend on one single-valued reference.

    Values that make the same members true are interchangeable and share
    one variable, which means "the reference has one of these values".  At
    most one variable is true, at least one is true when the reference is a
    parameter with AllowedValues, and each Fn::Equals is true exactly when
    one of its values' variables is."""
    domain = set(allowed or ()).union(*(values for _, values in members))
    classes: dict[tuple[int, ...], None] = {}
    for value in sorted(domain):
        signature = tuple(n for n, (_, values) in enumerate(members) if value in values)
        classes[signature] = None

    # A member true for exactly one class serves as that class's variable.
    variables: dict[tuple[int, ...], Any] = {}
    for n, (equal_cnf, _) in enumerate(members):
        own = [key for key in classes if n in key]
        if len(own) == 1 and own[0] not in variables:
            variables[own[0]] = equal_cnf
    for n, key in enumerate(classes):
        variables.setdefault(key, Symbol(f"value:{ref_hash}:{n}"))

    _add_at_most_one(cnf, ref_hash, list(variables.values()))
    if allowed is not None:
        cnf.add_prop(Or(*variables.values()))
    for n, (equal_cnf, _) in enumerate(members):
        own = [v for signature, v in variables.items() if n in signature]
        if own != [equal_cnf]:
            add_equivalence(cnf, equal_cnf, Or(*own))


@dataclass(frozen=True)
class Conditions:
    conditions: dict[str, Condition] = field(init=True, default_factory=dict)
    # The template's condition definitions and parameter constraints.
    _base_cnf: EncodedCNF = field(init=True, default_factory=EncodedCNF, compare=False)
    # Every pinned condition, including those assumed by scenario enumeration.
    _pins: frozenset[tuple[str, bool]] = field(
        init=True, default_factory=frozenset, compare=False
    )
    # The pins that are facts at this point in the template (resource/output
    # Condition, enclosing Fn::If).  Pins only *assumed* by condition-scenario
    # enumeration (see evolve(assumed=True)) are left out.  Reachability
    # questions (W1028) must be answered against these so that a value merely
    # being explored by enumeration is not mistaken for an impossible one.
    _hard_pins: frozenset[tuple[str, bool]] = field(
        init=True, default_factory=frozenset, compare=False
    )
    _condition_symbols: dict[str, Symbol] = field(
        init=True, default_factory=dict, compare=False
    )
    # Whether a set of pins is satisfiable.  The answer holds only for this
    # _base_cnf, so pass the dict on only together with it (evolve does).
    _satisfiable: dict[frozenset[tuple[str, bool]], bool] = field(
        init=True, default_factory=dict, compare=False, repr=False
    )
    _max_scenarios: int = field(init=False, default=128)
    _max_pin_attempts: int = field(init=False, default=2048)

    @property
    def cnf(self) -> EncodedCNF:
        """The template's condition clauses plus every pin, as a new copy."""
        return self._cnf_with(self._pins)

    @property
    def hard_cnf(self) -> EncodedCNF:
        """The template's condition clauses plus the hard pins, as a new copy."""
        return self._cnf_with(self._hard_pins)

    def _cnf_with(self, pins: frozenset[tuple[str, bool]]) -> EncodedCNF:
        cnf = self._base_cnf.copy()
        for name, value in sorted(pins):
            sym = self._condition_symbols[name]
            cnf.add_prop(sym if value else Not(sym))
        return cnf

    def _is_satisfiable(self, pins: frozenset[tuple[str, bool]]) -> bool:
        if pins not in self._satisfiable:
            self._satisfiable[pins] = bool(satisfiable(self._cnf_with(pins)))
        return self._satisfiable[pins]

    @classmethod
    def create_from_instance(
        cls,
        conditions: Any,
        rules: dict[str, dict],
        parameters: dict[str, "Parameter"],
        mappings: Any = None,
    ) -> "Conditions":
        obj: dict[str, Condition] = {}
        if not isinstance(conditions, dict):
            raise ValueError("Conditions must be a object")
        for k, v in conditions.items():
            if not isinstance(k, str):
                # Condition logical IDs must be strings (rule E8001 reports
                # non-string names).  Skip them here so the sympy Symbol
                # table below never receives a non-string name, which would
                # raise TypeError before any rule gets to run.
                continue
            try:
                other_conditions = conditions.copy()
                del other_conditions[k]
                obj[k] = Condition.create_from_instance(v, other_conditions)
            except ValueError:
                obj[k] = Condition.create_from_instance(
                    {"Fn::Equals": [None, None]}, conditions
                )

        # Build EncodedCNF with a Symbol per condition name
        cnf = EncodedCNF()
        condition_symbols: dict[str, Symbol] = {}
        for name, cond in obj.items():
            sym = Symbol(name)
            condition_symbols[name] = sym
            # Add equivalence: Symbol(name) <-> condition's boolean expression
            add_equivalence(cnf, sym, cond.cnf)

        # A condition's equals includes those of every condition it references,
        # so visit each distinct Fn::Equals once (#4984).
        distinct_equals: dict[str, Equal] = {}
        for _, c_v in obj.items():
            for i in c_v.equals:
                distinct_equals.setdefault(i.hash, i)

        # A single-valued reference (a parameter, a pseudo-parameter such as
        # AWS::Region, or any expression compared to strings) takes one value,
        # so the Fn::Equals that depend on it are constrained together
        # (issues #4799, #5044).  The raw Mappings section is read: the
        # context Mappings drops non-string keys, and a dropped key could be
        # the one a Ref resolves to.
        if not isinstance(mappings, dict):
            mappings = {}
        equals_by_ref: dict[str, list[tuple[Symbol, frozenset[str]]]] = {}
        for i in distinct_equals.values():
            for ref_hash, values in _true_values(i, mappings):
                equals_by_ref.setdefault(ref_hash, []).append((i.cnf, values))

        allowed_by_ref = _allowed_values_by_ref(parameters)
        for ref_hash, members in equals_by_ref.items():
            _add_value_constraints(cnf, ref_hash, members, allowed_by_ref.get(ref_hash))

        return cls(
            conditions=obj,
            _base_cnf=cnf,
            _condition_symbols=condition_symbols,
        )

    def evolve(self, status: dict[str, bool], assumed: bool = False) -> "Conditions":
        """Pin one or more conditions to a value.

        When ``assumed`` is True the pin is recorded only in the pins (used for
        pruning impossible scenarios) and not in the hard pins.  This is used by
        condition-scenario enumeration, which explores both values of a
        condition; those values are hypotheses, not facts, so a branch that
        merely disagrees with the scenario currently being enumerated must not
        be reported as unreachable.
        """
        cls = self.__class__

        if not status:
            return self

        all_same = True
        for condition, condition_status in status.items():
            if (
                condition in self.conditions
                and self.conditions[condition].status != condition_status
            ):
                all_same = False
                break
        if all_same:
            return self

        conditions: dict[str, Condition] = {}
        pins: set[tuple[str, bool]] = set()
        hard_pins = set(self._hard_pins)
        for condition, value in self.conditions.items():
            s = status.get(condition, value.status)
            try:
                conditions[condition] = value.evolve(status=s)
                if s is not None and condition in self._condition_symbols:
                    pins.add((condition, s))
                    # Only the conditions being pinned by *this* call, and only
                    # when they are facts (not enumeration hypotheses), join
                    # the hard pins.  Conditions carried over from a prior
                    # evolve are already there if they were facts, and must
                    # stay out if they were assumptions.
                    if not assumed and condition in status:
                        hard_pins.add((condition, s))
            except ValueError as e:
                raise Unsatisfiable(
                    new_status=status,
                    current_status=self.status,
                ) from e

        new_pins = frozenset(pins)
        if not self._is_satisfiable(new_pins):
            raise Unsatisfiable(
                new_status=status,
                current_status=self.status,
            )

        return cls(
            conditions=conditions,
            _base_cnf=self._base_cnf,
            _pins=new_pins,
            _hard_pins=frozenset(hard_pins),
            _condition_symbols=self._condition_symbols,
            _satisfiable=self._satisfiable,
        )

    def is_reachable(self, name: str, value: bool) -> bool:
        """Return whether ``name`` can take ``value`` given the forced facts.

        This is answered against the hard pins so that a condition merely being
        explored by scenario enumeration is not treated as impossible.  An
        unknown condition is conservatively considered reachable.
        """
        if name not in self._condition_symbols:
            return True
        return self._is_satisfiable(self._hard_pins | {(name, value)})

    def _build_conditions(self, conditions: set[str]) -> Iterator["Conditions"]:
        """Yield up to ``_max_scenarios`` satisfiable scenarios.

        Conditions are pinned one at a time, True before False, so scenarios
        come in the same order as ``itertools.product``.  A set of pins that
        is unsatisfiable is skipped with every scenario that extends it.
        Every satisfiable set of pins extends to at least one scenario, so the
        first scenario is found within two pins per condition, and the search
        stops after ``_max_pin_attempts`` pins.
        """
        names = list(conditions)
        yielded = 0
        attempts = 0

        def scenarios(i: int, current: "Conditions") -> Iterator["Conditions"]:
            nonlocal yielded, attempts
            if i == len(names):
                yielded += 1
                yield current
                return
            name = names[i]
            for value in (True, False):
                # On occasions people will use a lot of non-related conditions
                # this is fail safe to limit the maximum number of responses
                # and the pins tried to find them
                if yielded >= self._max_scenarios or attempts >= self._max_pin_attempts:
                    return
                attempts += 1
                try:
                    scenario = current.evolve({name: value}, assumed=True)
                except Unsatisfiable:
                    # evolve only returns satisfiable pins, so when one value
                    # is unsatisfiable the other is satisfiable and needs no
                    # solver call.  self may not have been solved yet.
                    if current is not self:
                        self._satisfiable[current._pins | {(name, not value)}] = True
                    continue
                yield from scenarios(i + 1, scenario)

        yield from scenarios(0, self)

    def evolve_from_instance(
        self, instance: Any, context: "Context"
    ) -> Iterator[tuple[Any, "Conditions"]]:
        conditions = get_conditions_from_property(instance)

        for scenario in self._build_conditions(conditions):
            yield (
                build_instance_from_scenario(
                    instance,
                    scenario.status,
                    is_root=True,
                    context=context,
                ),
                scenario,
            )

    @property
    def status(self) -> dict[str, bool]:
        obj = {}
        for name, c in self.conditions.items():
            if c.status is not None:
                obj[name] = c.status

        return obj
