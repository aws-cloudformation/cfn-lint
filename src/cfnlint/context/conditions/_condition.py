"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sympy import And, Not, Or
from sympy.logic.boolalg import BooleanFunction

from cfnlint.conditions._utils import get_hash
from cfnlint.context.conditions._equals import Equal
from cfnlint.helpers import FUNCTION_CONDITIONS, is_function


@dataclass(frozen=True)
class Condition:
    instance: Any = field(init=True)
    status: bool | None = field(init=True, default=None)
    hash: str = field(init=False)

    fn_equals: Equal | None = field(init=True, default=None)
    condition: list["Condition"] | "Condition" | None = field(init=True, default=None)
    cnf: BooleanFunction = field(init=True, default_factory=BooleanFunction)

    def __post_init__(self):
        object.__setattr__(self, "hash", get_hash(self.instance))

    @classmethod
    def create_from_instance(
        cls, instance: Any, all_conditions: dict[str, Any]
    ) -> "Condition":
        fn_k, fn_v = is_function(instance)
        if fn_k is None:
            raise ValueError("Condition value must be an object of length 1")
        if fn_k in FUNCTION_CONDITIONS:
            if not isinstance(fn_v, list):
                raise ValueError(f"{fn_v!r} value should be an array")
            if fn_k == "Fn::Equals":
                equal = Equal.create_from_instance(fn_v)
                return cls(instance=instance, fn_equals=equal, cnf=equal.cnf)

            condition = []
            for v in fn_v:
                condition.append(Condition.create_from_instance(v, all_conditions))

            cnf = None
            if fn_k == "Fn::And":
                cnf = And(*[c.cnf for c in condition])
            elif fn_k == "Fn::Or":
                cnf = Or(*[c.cnf for c in condition])
            elif fn_k == "Fn::Not":
                if len(condition) != 1:
                    raise ValueError(
                        f"Fn::Not expects only one condition, got {len(condition)}"
                    )
                cnf = Not(condition[0].cnf)

            return cls(instance=instance, condition=condition, cnf=cnf)

        if fn_k == "Condition":
            if not isinstance(fn_v, str):
                raise ValueError(f"Condition value {fn_v!r} must be a string")
            sub_condition = all_conditions.get(fn_v)
            try:
                sub_all_conditions = all_conditions.copy()
                del sub_all_conditions[fn_v]
                c = Condition.create_from_instance(sub_condition, sub_all_conditions)
            except Exception:
                c = Condition.create_from_instance(
                    {"Fn::Equals": [None, None]}, all_conditions
                )
            return cls(instance=instance, condition=c, cnf=c.cnf)

        raise ValueError(f"Unknown key {fn_k!r} in condition")

    def evolve(self, status: bool | None) -> "Condition":
        cls = self.__class__

        if self.status is not None:
            if status != self.status:
                raise ValueError(f"Resetting status to {status} from {self.status}")

        return cls(
            instance=self.instance,
            status=status,
            cnf=self.cnf,
        )

    @property
    def is_region(self) -> bool:
        """Returns True or False if the condition is based on region

        Args: None

        Returns:
            bool
                Returns True or False if the condition is based on region
        """
        if self.fn_equals:
            return self.fn_equals.is_region
        if isinstance(self.condition, list):
            for c in self.condition:
                if c.is_region:
                    return True
            return False
        if self.condition:
            return self.condition.is_region
        return False

    @property
    def equals(self) -> list[Equal]:
        """Returns a Sequence of the Equals that make up the Condition

        Args: None

        Returns:
            Sequence[EqualParameter] | Sequence[Equal] | None:
                The Equal that are part of the condition
        """
        if self.fn_equals:
            return [self.fn_equals]
        if isinstance(self.condition, list):
            equals = []
            for c in self.condition:
                equals.extend(c.equals)
            return equals
        if self.condition:
            return self.condition.equals
        return []
