"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterator

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

if TYPE_CHECKING:
    from cfnlint.context.context import Context, Parameter


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

        # NAND: two Fn::Equals comparing the same single-valued reference
        # (a parameter, with or without AllowedValues, or a pseudo-parameter
        # such as AWS::Region or AWS::AccountId) to different static values
        # cannot both be true. Previously this constraint was only added
        # inside the AllowedValues loop below, so plain parameters and
        # pseudo-parameters never got it (issue #4799).
        equals_by_ref: dict[str, list[tuple[Symbol, str]]] = {}
        for i in distinct_equals.values():
            if not isinstance(i.left.instance, str):
                continue
            if not isinstance(i.right.instance, dict):
                continue
            seen = equals_by_ref.setdefault(i.right.hash, [])
            for prev_cnf, prev_val in seen:
                if prev_val != i.left.instance:
                    cnf.add_prop(~(i.cnf & prev_cnf))
            seen.append((i.cnf, i.left.instance))

        # Add parameter AllowedValues constraints
        for p_k, p_v in parameters.items():
            if not p_v.allowed_values:
                continue
            allowed_values = p_v.allowed_values.copy()
            p_hash = get_hash({"Ref": p_k})
            equals_cnfs: list[Symbol] = []
            for i in distinct_equals.values():
                if i.right.hash == p_hash:
                    if not isinstance(i.left.instance, str):
                        continue
                    equals_cnfs.append(i.cnf)
                    if i.left.instance in allowed_values:
                        allowed_values.remove(i.left.instance)

            if not allowed_values and equals_cnfs:
                cnf.add_prop(Or(*equals_cnfs))

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
        scenarios_attempted = 0
        for product in itertools.product([True, False], repeat=len(conditions)):
            params = dict(zip(conditions, product))
            try:
                yield self.evolve(params, assumed=True)
            except Unsatisfiable:
                pass

            scenarios_attempted += 1
            # On occassions people will use a lot of non-related conditions
            # this is fail safe to limit the maximum number of responses
            if scenarios_attempted >= self._max_scenarios:
                return

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
