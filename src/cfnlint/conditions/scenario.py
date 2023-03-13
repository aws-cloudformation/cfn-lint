from typing import Dict


class Scenario:
    def __init__(self) -> None:
        self._condition_result: Dict[str, bool] = {}

    def add_condition(self, name: str, result: bool) -> None:
        self._condition_result[name] = result
