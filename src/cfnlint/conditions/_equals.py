"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
import logging
from typing import Any, Mapping, Tuple

from sympy import Symbol
from sympy.logic.boolalg import BooleanFalse, BooleanTrue

from cfnlint.conditions._utils import get_hash
from cfnlint.helpers import is_function

LOGGER = logging.getLogger(__name__)
REF_REGION = get_hash({"Ref": "AWS::Region"})


class EqualParameter:
    hash: str = ""

    def __init__(self, value: dict):
        self._value = value
        k, _ = is_function(value)

        # we can only do satisfaction validation
        # on Refs currently
        if k not in ["Ref"]:
            self._satisfiable = False
        else:
            self._satisfiable = True

        self.hash: str = get_hash(value)

    def __eq__(self, __o: Any):
        if isinstance(__o, str):
            return self.hash == __o
        return self.hash == __o.hash

    @property
    def satisfiable(self) -> bool:
        """Returns a boolean value if the parameter can be True or False

        Args: None

        Returns:
            bool: True if the parameter can be True or False, False otherwise
        """
        return self._satisfiable


class Equal:
    hash: str
    _left: EqualParameter | str
    _right: EqualParameter | str
    _is_static: bool | None
    _is_region: Tuple[bool, str]

    def __init__(self, equal: list[str | dict]) -> None:
        self._is_static = None
        if isinstance(equal, list) and len(equal) == 2:
            # sort to keep consistancy from random ordering
            # pylint: disable=unnecessary-lambda
            equal_s = sorted(equal, key=lambda value: json.dumps(value))

            self._left = self._init_parameter(equal_s[0])
            self._right = self._init_parameter(equal_s[1])

            self.hash = get_hash([self._left, self._right])
            if isinstance(self._left, str) and isinstance(self._right, str):
                self._is_static = self._left == self._right
            elif isinstance(self._left, EqualParameter) and isinstance(
                self._right, EqualParameter
            ):
                if self._left == self._right:
                    self._is_static = True

            self._is_region = (False, "")
            if isinstance(self._left, EqualParameter):
                if self._left.hash == REF_REGION and isinstance(self._right, str):
                    self._is_region = (True, self._right)
            if isinstance(self._right, EqualParameter):
                if self._right.hash == REF_REGION and isinstance(self._left, str):
                    self._is_region = (True, self._left)

            return
        raise ValueError("Equals has to be a list of two values")

    def _init_parameter(self, parameter: dict[str, Any] | str) -> EqualParameter | str:
        if isinstance(parameter, dict):
            return EqualParameter(parameter)
        return str(parameter)

    @property
    def is_static(self) -> bool | None:
        """Returns a boolean value if the result is always True or False or None if
            it isn't a static boolean

        Args: None

        Returns:
            bool | None: None if the equals can be True or False or True/False if
            the equals will always return the same result
        """
        return self._is_static

    @property
    def parameters(self) -> list[EqualParameter]:
        """Returns a List of the EqualParameter that make up the Condition

        Args: None

        Returns:
            list[Equal]: A list of the left and right equal parameters if they are
                         of type EqualParameter
        """
        params = []
        if isinstance(self._left, EqualParameter):
            params.append(self._left)
        if isinstance(self._right, EqualParameter):
            params.append(self._right)
        return params

    @property
    def is_region(self) -> Tuple[bool, str]:
        """Returns a Tuple if the condition is comparing a region to a string

        Args: None

        Returns:
            Tuple[bool, str]: Tuple where the boolean is True if the condition
              is using Ref: AWS::Region and the second element is for the region
              being compared
        """
        return self._is_region

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def build_cnf(
        self, params: dict[str, Symbol]
    ) -> BooleanTrue | BooleanFalse | Symbol:
        """Build a SymPy CNF solver based on the provided params
        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy Symbol
        Returns:
            BooleanFunction: A Not SymPy BooleanFunction
        """
        if self._is_static is not None:
            if self._is_static:
                return BooleanTrue()
            return BooleanFalse()

        return params.get(self.hash, Symbol(self.hash))

    def test(self, scenarios: Mapping[str, str]) -> bool:
        """Do an equals based on the provided scenario"""
        if self._is_static in [True, False]:
            return self._is_static
        for scenario, value in scenarios.items():
            if isinstance(self._left, EqualParameter):
                if scenario == self._left:
                    return value == self._right
            if isinstance(self._right, EqualParameter):
                if scenario == self._right:
                    return value == self._left

        raise ValueError("An appropriate scenario was not found")
