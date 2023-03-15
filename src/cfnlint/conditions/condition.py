from typing import Any, Dict, List, Optional, Union

from z3 import And, Not, Or

from cfnlint.conditions.equals import Equal, EqualParameter


class Condition:
    """The generic class to represent any type of Condition"""

    def __init__(self) -> None:
        self._fn_equals: Optional[Equal] = None
        self._condition: Optional[Union[ConditionList, ConditionNamed]] = None

    def _init_condition(
        self, condition: Dict[str, dict], all_conditions: Dict[str, dict]
    ) -> None:
        if len(condition) == 1:
            for k, v in condition.items():
                if k == "Fn::Equals":
                    self._fn_equals = Equal(v)
                elif k == "Fn::And":
                    self._condition = ConditionAnd(v, all_conditions)
                elif k == "Fn::Or":
                    self._condition = ConditionOr(v, all_conditions)
                elif k == "Fn::Not":
                    self._condition = ConditionNot(v, all_conditions)
                elif k == "Condition":
                    self._condition = ConditionNamed(v, all_conditions)
                else:
                    raise ValueError(f"Unknown key ({k}) in condition")
        else:
            raise ValueError("Condition value must be an object of length 1")

    def get_equals(self) -> List[Equal]:
        """Returns a List of the Equals that make up the Condition

        Args: None

        Returns:
            List[Equal]: The Equal that are part of the condition
        """
        if self._fn_equals:
            return [self._fn_equals]
        if self._condition:
            return self._condition.get_equals()
        return []

    def build_solver(self, params: Dict[str, Any]) -> Any:
        """Build a z3 solver based on the provided params

        Args:
            params Dict[str, Any]: params is a dict that represents
                    the the hash of an Equal and the z3 boolean equation

        Returns:
            Any: Any number of different z3 solver equations
        """
        if self._condition:
            return self._condition.build_solver(params)
        if self._fn_equals:
            return params.get(self._fn_equals.hash)
        return None


class ConditionList(Condition):
    """The generic class to represent any type of List condition
    List conditions are And, Or, Not
    """

    def __init__(self, conditions: List[dict], all_conditions) -> None:
        super().__init__()
        self._conditions: List[ConditionUnnammed] = []
        self._prefix_path: str = ""
        for condition in conditions:
            self._conditions.append(ConditionUnnammed(condition, all_conditions))

    def get_equals(self) -> List[EqualParameter]:
        """Returns a List of the Equals that make up the Condition

        Args: None

        Returns:
            List[Equal]: The Equal that are part of the condition
        """
        equals: List[Equal] = []
        for condition in self._conditions:
            equals.extend(condition.get_equals())
        return equals


class ConditionAnd(ConditionList):
    """Represents the logic specific to an And Condition"""

    def __init__(self, conditions: List[dict], all_conditions: Dict) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::And"

    def build_solver(self, params: Dict[str, Any]) -> Any:
        """Build a z3 solver based on the provided params
        Args:
            params Dict[str, Any]: params is a dict that represents
                    the the hash of an Equal and the z3 boolean equation
        Returns:
            Any: Any number of different z3 solver equations
        """
        conditions: List[Any] = []
        for child in self._conditions:
            conditions.append(child.build_solver(params))

        return And(conditions)


class ConditionNot(ConditionList):
    """Represents the logic specific to an Not Condition"""

    def __init__(self, conditions: List[dict], all_conditions: Dict) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::Not"
        if len(conditions) != 1:
            raise ValueError("Condition length must be 1")

    def build_solver(self, params: Dict[str, Any]) -> Any:
        """Build a z3 solver based on the provided params
        Args:
            params Dict[str, Any]: params is a dict that represents
                    the the hash of an Equal and the z3 boolean equation
        Returns:
            Any: Any number of different z3 solver equations
        """
        return Not(self._conditions[0].build_solver(params))


class ConditionOr(ConditionList):
    """Represents the logic specific to an Or Condition"""

    def __init__(self, conditions: List[dict], all_conditions: Dict) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::Or"

    def build_solver(self, params: Dict[str, Any]) -> Any:
        """Build a z3 solver based on the provided params
        Args:
            params Dict[str, Any]: params is a dict that represents
                    the the hash of an Equal and the z3 boolean equation
        Returns:
            Any: Any number of different z3 solver equations
        """
        conditions: List[Any] = []
        for child in self._conditions:
            conditions.append(child.build_solver(params))
        return Or(conditions)


class ConditionUnnammed(Condition):
    """Represents an unnamed condition which is basically a nested Equals"""

    def __init__(self, condition: Any, all_conditions: Dict) -> None:
        super().__init__()
        self._equals = []
        if isinstance(condition, dict):
            self._init_condition(condition, all_conditions)
        else:
            raise ValueError("Condition must have a value that is an object")


class ConditionNamed(Condition):
    """The parent condition that directly represents a named condition in a template"""

    def __init__(self, name: str, all_conditions: Dict) -> None:
        super().__init__()
        self._equals = []
        condition = all_conditions.get(name)
        if isinstance(condition, dict):
            self._name = name
            self._init_condition(condition, all_conditions)
        else:
            raise ValueError(f"Condition {name} must have a value that is an object")

    def build_true_solver(self, params: Dict[str, Any]) -> Any:
        """Build a z3 solver for a True based scenario
        Args:
            params Dict[str, Any]: params is a dict that represents
                    the the hash of an Equal and the z3 boolean equation
        Returns:
            Any: a z3 solver equation
        """
        return self.build_solver(params)

    def build_false_solver(self, params: Dict[str, Any]) -> Any:
        """Build a z3 solver for a False based scenario
        Args:
            params Dict[str, Any]: params is a dict that represents
                    the the hash of an Equal and the z3 boolean equation
        Returns:
            Any: a z3 solver equation
        """
        return Not(self.build_true_solver(params))
