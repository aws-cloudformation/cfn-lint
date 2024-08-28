"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence, Union

from sympy import And, Not, Or, Symbol
from sympy.logic.boolalg import BooleanFunction

from cfnlint.conditions._condition import (
    Condition,
    ConditionAnd,
    ConditionList,
    ConditionNamed,
    ConditionNot,
    ConditionOr,
    ConditionUnnammed,
)
from cfnlint.conditions._equals import Equal
from cfnlint.helpers import FUNCTION_CONDITIONS

# we leave the type hinting here
_RULE = Dict[str, Any]


class Rule:

    def __init__(self, rule: _RULE, all_conditions: dict[str, dict]) -> None:
        self._fn_equals: Equal | None = None
        self._assertions: list[ConditionList | ConditionNamed] = []
        self._init_rule(rule, all_conditions)

    def _init_rule(
        self,
        rule: _RULE,
        all_conditions: dict[str, dict],
    ) -> None:
        for assertion in rule.get("Assertions", []):
            assert_ = assertion.get("Assert", {})
            if len(assert_) == 1:
                for k, v in assert_.items():
                    if k in FUNCTION_CONDITIONS:
                        if not isinstance(v, list):
                            raise ValueError(f"{k} value should be an array")
                        if k == "Fn::Equals":
                            self._fn_equals = Equal(v)
                        elif k == "Fn::And":
                            self._assertions.append(ConditionAnd(v, all_conditions))
                        elif k == "Fn::Or":
                            self._assertions.append(ConditionOr(v, all_conditions))
                        elif k == "Fn::Not":
                            self._assertions.append(ConditionNot(v, all_conditions))
                    elif k == "Condition":
                        if not isinstance(v, str):
                            raise ValueError(f"Condition value {v!r} must be a string")
                        self._assertions.append(ConditionNamed(v, all_conditions))
                    else:
                        raise ValueError(f"Unknown key ({k}) in condition")
            else:
                raise ValueError("Condition value must be an object of length 1")

    @property
    def equals(self) -> list[Equal]:
        """Returns a Sequence of the Equals that make up the Condition

        Args: None

        Returns:
            Sequence[EqualParameter] | Sequence[Equal] | None:
                The Equal that are part of the condition
        """
        if self._fn_equals:
            return [self._fn_equals]
        if self._assertions:
            _equals = []
            for assertion in self._assertions:
                _equals.append(assertion.equals)
            return _equals
        return []

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction | Symbol | None:
        """Build a SymPy CNF based on the provided params

        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy Symbols

        Returns:
            Any: Any number of different SymPy CNF clauses
        """
        if self._assertions:
            assertions = []
            for assertion in self._assertions:
                assertions.append(assertion.build_cnf(params))
            return And(*assertions)
        if self._fn_equals:
            return params.get(self._fn_equals.hash)
        return None

    def _test(self, scenarios: Mapping[str, str]) -> bool:
        if self._fn_equals:
            return self._fn_equals.test(scenarios)
        if self._assertions:
            for assertion in self._assertions:
                if not assertion._test(scenarios):
                    return False

            return True
        return False
