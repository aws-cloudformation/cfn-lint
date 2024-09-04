"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence, Union

from sympy import And, Not, Or, Symbol
from sympy.logic.boolalg import BooleanFunction, BooleanTrue

from cfnlint.conditions._equals import Equal
from cfnlint.helpers import FUNCTION_CONDITIONS

# we leave the type hinting here
_CONDITION = Dict[str, Union[str, Sequence["_CONDITION"]]]


class Condition:
    """The generic class to represent any type of Condition"""

    def __init__(self) -> None:
        self._fn_equals: Equal | None = None
        self._condition: ConditionList | ConditionNamed | None = None

    def _init_condition(
        self,
        condition: _CONDITION,
        all_conditions: dict[str, dict],
    ) -> None:
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
        if self._condition:
            return self._condition.equals
        return []

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction | Symbol | None:
        """Build a SymPy CNF based on the provided params

        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy Symbols

        Returns:
            Any: Any number of different SymPy CNF clauses
        """
        if self._condition:
            return self._condition.build_cnf(params)
        if self._fn_equals:
            return self._fn_equals.build_cnf(params)
        return BooleanTrue()

    def _test(self, scenarios: Mapping[str, str]) -> bool:
        if self._fn_equals:
            return self._fn_equals.test(scenarios)
        if self._condition:
            # pylint: disable=W0212
            return self._condition._test(scenarios)
        return False


class ConditionList(Condition):
    """The generic class to represent any type of List condition
    List conditions are And, Or, Not
    """

    def __init__(
        self, conditions: Sequence[_CONDITION], all_conditions: dict[str, dict]
    ) -> None:
        super().__init__()
        self._conditions: list[ConditionUnnammed] = []
        self._prefix_path: str = ""
        for condition in conditions:
            self._conditions.append(ConditionUnnammed(condition, all_conditions))

    @property
    def equals(self) -> list[Equal]:
        """Returns a List of the Equals that make up the Condition

        Args: None

        Returns:
            list[Equal]: The Equal that are part of the condition
        """
        equals: list[Equal] = []
        for condition in self._conditions:
            equals.extend(condition.equals)
        return equals


class ConditionAnd(ConditionList):
    """Represents the logic specific to an And Condition"""

    def __init__(
        self, conditions: Sequence[_CONDITION], all_conditions: dict[str, dict]
    ) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::And"

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction:
        """Build a SymPy CNF solver based on the provided params
        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy Symbols
        Returns:
            BooleanFunction: An And SymPy BooleanFunction
        """
        conditions: list[Any] = []
        for child in self._conditions:
            conditions.append(child.build_cnf(params))

        return And(*conditions)

    def _test(self, scenarios: Mapping[str, str]) -> bool:
        # pylint: disable=W0212
        return all(condition._test(scenarios) for condition in self._conditions)


class ConditionNot(ConditionList):
    """Represents the logic specific to an Not Condition"""

    def __init__(
        self, conditions: Sequence[_CONDITION], all_conditions: dict[str, dict]
    ) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::Not"
        if len(conditions) != 1:
            raise ValueError("Condition length must be 1")

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction:
        """Build a SymPy CNF solver based on the provided params
        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy Symbol
        Returns:
            BooleanFunction: A Not SymPy BooleanFunction
        """
        return Not(self._conditions[0].build_cnf(params))

    def _test(self, scenarios: Mapping[str, str]) -> bool:
        # pylint: disable=W0212
        return not any(condition._test(scenarios) for condition in self._conditions)


class ConditionOr(ConditionList):
    """Represents the logic specific to an Or Condition"""

    def __init__(
        self, conditions: Sequence[_CONDITION], all_conditions: dict[str, dict]
    ) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::Or"

    def build_cnf(self, params: dict[str, Symbol]) -> BooleanFunction:
        """Build a SymPy CNF solver based on the provided params
        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy Symbols
        Returns:
            BooleanFunction: An Or SymPy BooleanFunction
        """
        conditions: list[Any] = []
        for child in self._conditions:
            conditions.append(child.build_cnf(params))
        return Or(*conditions)

    def _test(self, scenarios: Mapping[str, str]) -> bool:
        # pylint: disable=W0212
        return any(condition._test(scenarios) for condition in self._conditions)


class ConditionUnnammed(Condition):
    """Represents an unnamed condition which is basically a nested Equals"""

    def __init__(self, condition: Any, all_conditions: dict[str, dict]) -> None:
        super().__init__()
        if isinstance(condition, dict):
            self._init_condition(condition, all_conditions)
        else:
            raise ValueError("Condition must have a value that is an object")


class ConditionNamed(Condition):
    """The parent condition that directly represents a named condition in a template"""

    def __init__(self, name: str, all_conditions: dict[str, dict]) -> None:
        super().__init__()
        condition = all_conditions.get(name)
        if isinstance(condition, dict):
            self._name = name
            self._init_condition(condition, all_conditions)
        else:
            raise ValueError(f"Condition {name} must have a value that is an object")

    def build_true_cnf(self, params: dict[str, Symbol]) -> Any:
        """Build a SymPy CNF for a True based scenario
        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy Symbols
        Returns:
            Any: A SymPy CNF clause
        """
        return self.build_cnf(params)

    def build_false_cnf(self, params: dict[str, Symbol]) -> Any:
        """Build a SymPy CNF for a False based scenario
        Args:
            params dict[str, Symbol]: params is a dict that represents
                    the hash of an Equal and the SymPy CNF Symbols
        Returns:
            Any: A Not SymPy CNF clause
        """
        return Not(self.build_true_cnf(params))

    def test(self, scenarios: Mapping[str, str]) -> bool:
        """Test a condition based on a scenario"""
        return self._test(scenarios)
