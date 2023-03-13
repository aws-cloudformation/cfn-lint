import dataclasses
from z3 import Solver, Not, And, Or
from typing import Any, Optional, List, Dict, Union, Tuple
from cfnlint.conditions.equals import Equal, EqualParameter
from cfnlint.conditions.scenario import Scenario
from copy import deepcopy


@dataclasses.dataclass
class ConditionPath:
    condition: Any
    path: List[Union[str, int]]


class Condition:
    def __init__(self) -> None:
        self._fn_equals: Optional[Equal] = None
        self._fn_and: Optional[ConditionAnd] = None
        self._fn_or: Optional[ConditionOr] = None
        self._fn_not: Optional[Condition] = None
        self._condition: Optional[ConditionNamed] = None

    def _init_condition(
        self, condition: Dict[str, dict], all_conditions: Dict[str, dict]
    ) -> None:
        if len(condition) == 1:
            for k, v in condition.items():
                if k == "Fn::Equals":
                    self._fn_equals = Equal(v)
                elif k == "Fn::And":
                    self._fn_and = ConditionAnd(v, all_conditions)
                elif k == "Fn::Or":
                    self._fn_or = ConditionOr(v, all_conditions)
                elif k == "Fn::Not":
                    self._fn_not = ConditionNot(v, all_conditions)
                elif k == "Condition":
                    self._condition = ConditionNamed(v, all_conditions)
                else:
                    raise ValueError(f"Unknown key ({k}) in condition")
        else:
            raise ValueError(f"Condition value must be an object of length 1")

    def get_parameters(self) -> List[EqualParameter]:
        if self._fn_equals:
            return self._fn_equals.get_parameters()
        if self._fn_not:
            return self._fn_not.get_parameters()
        if self._fn_and:
            return self._fn_and.get_parameters()
        if self._fn_or:
            return self._fn_or.get_parameters()
        if self._condition:
            return self._condition.get_parameters()
        return []

    def get_equals(self) -> List[Equal]:
        if self._fn_equals:
            return [self._fn_equals]
        if self._fn_not:
            return self._fn_not.get_equals()
        if self._fn_and:
            return self._fn_and.get_equals()
        if self._fn_or:
            return self._fn_or.get_equals()
        if self._condition:
            return self._condition.get_equals()
        return []

    def get_children(self) -> List[ConditionPath]:
        if self._fn_not:
            return self._fn_not.get_children()
        if self._fn_and:
            return self._fn_and.get_children()
        if self._fn_or:
            return self._fn_or.get_children()
        if self._condition:
            return [ConditionPath(self._condition, [])] + self._condition.get_children()
        return []

    def build_solver(self, vars: Dict[str, Any]) -> None:
        if self._fn_not:
            return self._fn_not.build_solver(vars)
        if self._fn_and:
            return self._fn_and.build_solver(vars)
        if self._fn_or:
            return self._fn_or.build_solver(vars)
        if self._condition:
            return self._condition.build_solver(vars)
        if self._fn_equals:
            return vars.get(self._fn_equals.hash)


class ConditionList(Condition):
    def __init__(self, conditions: List[dict], all_conditions) -> None:
        super().__init__()
        self._conditions: List[ConditionUnnammed] = []
        self._prefix_path: str = ""
        for condition in conditions:
            self._conditions.append(ConditionUnnammed(condition, all_conditions))

    def get_parameters(self) -> List[EqualParameter]:
        params: List[EqualParameter] = []
        for condition in self._conditions:
            params.extend(condition.get_parameters())
        return params

    def get_equals(self) -> List[EqualParameter]:
        equals: List[Equal] = []
        for condition in self._conditions:
            equals.extend(condition.get_equals())
        return equals

    def get_children(self) -> List[ConditionPath]:
        children: List[ConditionPath] = []
        for idx, condition in enumerate(self._conditions):
            for child in condition.get_children():
                child.path = [self._prefix_path, idx] + child.path
                children.append(child)
        return children


class ConditionAnd(ConditionList):
    def __init__(self, conditions: dict, all_conditions: Dict) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::And"

    def build_solver(self, vars: Dict[str, Any]) -> Any:
        conditions: List[Any] = []
        for child in self._conditions:
            conditions.append(child.build_solver(vars))

        return And(conditions)


class ConditionNot(ConditionList):
    def __init__(self, conditions: dict, all_conditions: Dict) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::Not"
        if len(conditions) != 1:
            ValueError("Condition length must be 1")

    def build_solver(self, vars: Dict[str, Any]) -> Any:
        for child in self._conditions:
            return Not(child.build_solver(vars))


class ConditionOr(ConditionList):
    def __init__(self, conditions: dict, all_conditions: Dict) -> None:
        super().__init__(conditions, all_conditions)
        self._prefix_path = "Fn::Or"

    def build_solver(self, vars: Dict[str, Any]) -> Any:
        conditions: List[Any] = []
        for child in self._conditions:
            conditions.append(child.build_solver(vars))
        return Or(conditions)


class ConditionUnnammed(Condition):
    def __init__(self, condition: Any, all_conditions: Dict) -> None:
        super().__init__()
        self._equals = []
        if isinstance(condition, dict):
            self._init_condition(condition, all_conditions)
        else:
            raise ValueError(f"Condition must have a value that is an object")


class ConditionNamed(Condition):
    def __init__(self, name: str, all_conditions: Dict) -> None:
        super().__init__()
        self._equals = []
        condition = all_conditions.get(name)
        if isinstance(condition, dict):
            self._name = name
            self._init_condition(condition, all_conditions)
        else:
            raise ValueError(f"Condition {name} must have a value that is an object")

    def __eq__(self, __o: object) -> bool:
        return self.__name == __o.name

    def __repr__(self) -> str:
        return self._name

    def build_true_solver(self, vars: Dict[str, Any]) -> Any:
        return self.build_solver(vars)

    def build_false_solver(self, vars: Dict[str, Any]) -> Any:
        return Not(self.build_solver(vars))
