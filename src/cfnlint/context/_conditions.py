"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Condition:
    instance: Any = field(init=True)
    status: bool | None = field(init=True, default=None)

    def evolve(self, status: bool | None) -> "Condition":
        cls = self.__class__

        if self.status is not None:
            if status != self.status:
                raise ValueError("Resetting status to condition")

        return cls(
            instance=self.instance,
            status=status,
        )


@dataclass(frozen=True)
class Conditions:
    # Template level condition management
    conditions: dict[str, Condition] = field(init=True, default_factory=dict)

    @classmethod
    def create_from_instance(cls, conditions: dict[str, Any]) -> "Conditions":
        obj = {}
        if not isinstance(conditions, dict):
            raise ValueError("Conditions must be a object")
        for k, v in conditions.items():
            try:
                obj[k] = Condition(v)
            except ValueError:
                pass

        return cls(conditions=obj)

    def evolve(self, status: dict[str, bool]) -> "Conditions":
        cls = self.__class__

        conditions: dict[str, Condition] = {}
        for condition, value in self.conditions.items():
            s = status.get(condition, value.status)
            try:
                conditions[condition] = value.evolve(status=s)
            except ValueError as e:
                raise ValueError(f"Error evolving condition {condition}") from e

        return cls(
            conditions=conditions,
        )

    @property
    def status(self) -> dict[str, bool]:
        obj = {}
        for name, c in self.conditions.items():
            if c.status is not None:
                obj[name] = c.status

        return obj
