"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterator

from sympy import Not, Or
from sympy.logic.boolalg import BooleanFunction
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
    # Template level condition management
    conditions: dict[str, Condition] = field(init=True, default_factory=dict)
    cnf: BooleanFunction | None = field(init=True, default=None)
    _max_scenarios: int = field(init=False, default=128)

    @classmethod
    def create_from_instance(
        cls, conditions: Any, rules: dict[str, dict], parameters: dict[str, "Parameter"]
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
                # this is a default condition so we can keep the name but it will
                # not associate with another condition and will always be true/false
                obj[k] = Condition.create_from_instance(
                    {"Fn::Equals": [None, None]}, conditions
                )

        cnf = None
        for p_k, p_v in parameters.items():

            if not p_v.allowed_values:
                continue
            allowed_values = p_v.allowed_values.copy()
            equals_cnfs = []
            for _, c_v in obj.items():
                for i in c_v.equals:
                    if i.right.hash == get_hash({"Ref": p_k}):
                        if not isinstance(i.left.instance, str):
                            continue
                        equals_cnfs.append(i.cnf)
                        if i.left.instance in allowed_values:
                            allowed_values.remove(i.left.instance)

            if not allowed_values:
                if cnf is None:
                    cnf = Or(*equals_cnfs)
                else:
                    cnf = cnf & Or(*equals_cnfs)

        return cls(conditions=obj, cnf=cnf)

    def evolve(self, status: dict[str, bool]) -> "Conditions":
        cls = self.__class__

        conditions: dict[str, Condition] = {}
        cnf = self.cnf
        for condition, value in self.conditions.items():
            s = status.get(condition, value.status)
            try:
                conditions[condition] = value.evolve(status=s)
                if s is not None:
                    if cnf:
                        cnf = (
                            cnf & conditions[condition].cnf
                            if s
                            else cnf & Not(conditions[condition].cnf)
                        )
                    else:
                        cnf = (
                            conditions[condition].cnf
                            if s
                            else Not(conditions[condition].cnf)
                        )
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
            yield build_instance_from_scenario(
                instance,
                scenario.status,
                is_root=True,
                context=context,
            ), scenario

    @property
    def status(self) -> dict[str, bool]:
        obj = {}
        for name, c in self.conditions.items():
            if c.status is not None:
                obj[name] = c.status

        return obj
