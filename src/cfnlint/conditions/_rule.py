"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from sympy import And, Implies, Symbol
from sympy.logic.boolalg import BooleanFunction, BooleanTrue

from cfnlint.conditions._condition import (
    ConditionAnd,
    ConditionList,
    ConditionNamed,
    ConditionNot,
    ConditionOr,
)
from cfnlint.conditions._equals import Equal
from cfnlint.helpers import FUNCTION_CONDITIONS

LOGGER = logging.getLogger(__name__)

# we leave the type hinting here
_RULE = Dict[str, Any]


class _Assertion:
    def __init__(self, condition: Any, all_conditions: dict[str, dict]) -> None:
        self._fn_equals: Equal | None = None
        self._condition: ConditionList | ConditionNamed | None = None

        if len(condition) == 1:
            for k, v in condition.items():
                if k in FUNCTION_CONDITIONS:
                    if not isinstance(v, list):
                        raise ValueError(f"{k} value should be an array")
                    if k == "Fn::Equals":
                        self._fn_equals = Equal(v)
                    elif k == "Fn::And":
                        self._condition = ConditionAnd(v, all_conditions)
                    elif k == "Fn::Or":
                        self._condition = ConditionOr(v, all_conditions)
                    elif k == "Fn::Not":
                        self._condition = ConditionNot(v, all_conditions)
                elif k == "Condition":
                    if not isinstance(v, str):
                        raise ValueError(f"Condition value {v!r} must be a string")
                    self._condition = ConditionNamed(v, all_conditions)
                else:
                    raise ValueError(f"Unknown key ({k}) in condition")
        else:
            raise ValueError("Condition value must be an object of length 1")

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction | Symbol | None:
        if self._fn_equals:
            try:
                return self._fn_equals.build_cnf(params)
            except Exception as e:
                LOGGER.debug(f"Error building condition: {e}")

        if self._condition:
            try:
                return self._condition.build_cnf(params)
            except Exception as e:
                LOGGER.debug(f"Error building condition: {e}")

        return BooleanTrue()

    @property
    def equals(self) -> list[Equal]:
        if self._fn_equals:
            return [self._fn_equals]
        if self._condition:
            return self._condition.equals
        return []


class _Assertions:
    def __init__(self, assertions: list[dict], all_conditions: dict[str, dict]) -> None:
        self._assertions: list[_Assertion] = []
        for assertion in assertions:
            assert_ = assertion.get("Assert", {})
            self._assertions.append(_Assertion(assert_, all_conditions))

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction | Symbol | None:

        assertions = []
        for assertion in self._assertions:
            assertions.append(assertion.build_cnf(params))

        try:
            return And(*assertions)
        except Exception as e:
            LOGGER.debug(f"Error building conditions: {e}")
            return BooleanTrue()

    @property
    def equals(self) -> list[Equal]:

        results = []
        for assertion in self._assertions:
            results.extend(assertion.equals)
        return results


class Rule:

    def __init__(self, rule: _RULE, all_conditions: dict[str, dict]) -> None:
        self._condition: _Assertion | None = None
        self._assertions: _Assertions | None = None
        self._init_rule(rule, all_conditions)

    def _init_rule(
        self,
        rule: _RULE,
        all_conditions: dict[str, dict],
    ) -> None:
        condition = rule.get("RuleCondition")
        if condition:
            self._condition = _Assertion(condition, all_conditions)

        assertions = rule.get("Assertions")
        if not assertions:
            raise ValueError("Rule must have Assertions")
        self._assertions = _Assertions(assertions, all_conditions)

    @property
    def equals(self) -> list[Equal]:
        result = []
        if self._condition:
            result.extend(self._condition.equals)
        if self._assertions:
            result.extend(self._assertions.equals)
        return result

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction | Symbol | None:

        if self._assertions:
            if self._condition:
                return Implies(
                    self._condition.build_cnf(params),
                    self._assertions.build_cnf(params),
                )
            return self._assertions.build_cnf(params)
        return None
