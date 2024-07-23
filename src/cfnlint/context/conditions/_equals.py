"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import cmp_to_key
from typing import Any

from sympy import Symbol

from cfnlint.conditions._utils import get_hash
from cfnlint.helpers import is_function

LOGGER = logging.getLogger(__name__)
REF_REGION = get_hash({"Ref": "AWS::Region"})


def _sorted(a: dict[str, str] | str, b: dict[str, str] | str) -> int:
    if isinstance(a, dict) and isinstance(b, dict):
        a_k, a_v = is_function(a)
        b_k, b_v = is_function(b)
        if a_k is None or b_k is None:
            if a_k is None and b_k is not None:
                return 1
            if a_k is not None and b_k is None:
                return -1
            return 0

        if a_k == "Ref" and isinstance(a_v, str):
            if b_k == "Ref" and isinstance(b_v, str):
                return -1 if a_v <= b_v else 1

        return -1 if a_k <= b_k else 1

    return -1 if str(a) <= str(b) else 1


_equals_cmp_key = cmp_to_key(_sorted)


@dataclass(frozen=True)
class EqualParameter:
    instance: dict[str, str] | str | None = field(init=True)
    hash: str = field(init=False)
    is_region: bool = field(init=False, default=False)

    def __post_init__(self):
        object.__setattr__(self, "hash", get_hash(self.instance))
        object.__setattr__(self, "is_region", self.hash == REF_REGION)

    @classmethod
    def create_from_instance(cls, instance: Any) -> "EqualParameter":
        if isinstance(instance, (str, bool, int, float)):
            return cls(instance=str(instance))

        if isinstance(instance, dict):
            return cls(instance=instance)

        # escape version
        if instance is None:
            return cls(instance=None)

        raise ValueError("EqualParameter has to be a string or a dict")

    def __eq__(self, __o: Any):
        if isinstance(__o, EqualParameter):
            return self.hash == __o.hash
        return False


@dataclass(frozen=True)
class Equal:
    instance: list[str | dict] = field(init=True)
    hash: str = field(init=False)

    left: EqualParameter = field(init=True)
    right: EqualParameter = field(init=True)

    is_static: bool | None = field(init=False, default=None)

    cnf: Symbol = field(init=False)

    @classmethod
    def create_from_instance(cls, instance: Any) -> "Equal":
        if not (isinstance(instance, list) and len(instance) == 2):
            raise ValueError("Equals has to be a list of two values")

        instance.sort(key=_equals_cmp_key)
        left = EqualParameter.create_from_instance(instance[0])
        right = EqualParameter.create_from_instance(instance[1])
        return cls(instance=instance, left=left, right=right)

    def __post_init__(self):
        object.__setattr__(self, "hash", get_hash(self.instance))
        if isinstance(self.left.instance, (str, int, bool, float)) and isinstance(
            self.right.instance, (str, int, bool, float)
        ):
            object.__setattr__(
                self, "is_static", self.left.instance == self.right.instance
            )
        object.__setattr__(self, "cnf", Symbol(self.hash))

    @property
    def parameters(self) -> list[EqualParameter]:
        """Returns a List of the EqualParameter that make up the Condition

        Args: None

        Returns:
            list[Equal]: A list of the left and right equal parameters if they are
                         of type EqualParameter
        """
        return [self.left, self.right]

    @property
    def is_region(self) -> bool:
        """
         Returns a bool if the condition is comparing a region to a string

        Args: None

        Returns:
            bool: If a parameter in the equals has {"Ref": "AWS::Region}
        """
        return (self.left.is_region or self.right.is_region) and not self.is_static
