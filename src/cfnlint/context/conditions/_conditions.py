"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterator

from sympy import Equivalent, Not, Or, Symbol
from sympy.assumptions.cnf import EncodedCNF
from sympy.logic.inference import satisfiable

from cfnlint.conditions._utils import get_hash
from cfnlint.context.conditions._condition import Condition
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
    cnf: EncodedCNF = field(init=True, default_factory=EncodedCNF, compare=False)
    _condition_symbols: dict[str, Symbol] = field(
        init=True, default_factory=dict, compare=False
    )
    _max_scenarios: int = field(init=False, default=128)

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
            cnf.add_prop(Equivalent(sym, cond.cnf))

        # Add parameter AllowedValues constraints
        for p_k, p_v in parameters.items():
            if not p_v.allowed_values:
                continue
            allowed_values = p_v.allowed_values.copy()
            equals_cnfs: list[tuple[Symbol, str]] = []
            for _, c_v in obj.items():
                for i in c_v.equals:
                    if i.right.hash == get_hash({"Ref": p_k}):
                        if not isinstance(i.left.instance, str):
                            continue
                        # NAND: two equals comparing the same param to
                        # different static values can't both be true
                        for prev_cnf, prev_val in equals_cnfs:
                            if prev_val != i.left.instance:
                                cnf.add_prop(~(i.cnf & prev_cnf))
                        equals_cnfs.append((i.cnf, i.left.instance))
                        if i.left.instance in allowed_values:
                            allowed_values.remove(i.left.instance)

            if not allowed_values and equals_cnfs:
                cnf.add_prop(Or(*[c for c, _ in equals_cnfs]))

        return cls(conditions=obj, cnf=cnf, _condition_symbols=condition_symbols)

    def evolve(self, status: dict[str, bool]) -> "Conditions":
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
        cnf = self.cnf.copy()
        for condition, value in self.conditions.items():
            s = status.get(condition, value.status)
            try:
                conditions[condition] = value.evolve(status=s)
                if s is not None and condition in self._condition_symbols:
                    sym = self._condition_symbols[condition]
                    cnf.add_prop(sym if s else Not(sym))
            except ValueError as e:
                raise Unsatisfiable(
                    new_status=status,
                    current_status=self.status,
                ) from e

        if not satisfiable(cnf):
            raise Unsatisfiable(
                new_status=status,
                current_status=self.status,
            )

        return cls(
            conditions=conditions,
            cnf=cnf,
            _condition_symbols=self._condition_symbols,
        )

    def _build_conditions(self, conditions: set[str]) -> Iterator["Conditions"]:
        scenarios_attempted = 0
        for product in itertools.product([True, False], repeat=len(conditions)):
            params = dict(zip(conditions, product))
            try:
                yield self.evolve(params)
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
