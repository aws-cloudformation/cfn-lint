import logging
from typing import List, Union, Dict, Any, Optional
from functools import cmp_to_key
import cfnlint.helpers
import json
from cfnlint.conditions._utils import get_hash
from cfnlint.conditions.exceptions import ConditionParseError

LOGGER = logging.getLogger(__name__)


class EqualParameter:
    hash: str = ""

    def __init__(self, value: dict):
        self._value = value
        self.hash: str = get_hash(value)

    def to_json(self):
        return json.dumps(self._value)

    def __eq__(self, __o: Any):
        return self.hash == __o.hash

    def __hash__(self):
        return hash(self.hash)


class Equal:
    hash: str
    _left: Union[EqualParameter, str]
    _right: Union[EqualParameter, str]

    def __init__(self, equal: List[Union[str, dict]]) -> None:
        if isinstance(equal, list) and len(equal) == 2:
            # sort to keep consistancy from random ordering
            equal_s = sorted(equal, key=lambda value: json.dumps(value))

            self._left = self._init_parameter(equal_s[0])
            self._right = self._init_parameter(equal_s[1])

            self.hash = get_hash([self._left, self._right])

    def _init_parameter(
        self, parameter: Union[Dict, str]
    ) -> Union[EqualParameter, str]:
        if isinstance(parameter, dict):
            return EqualParameter(parameter)
        elif isinstance(parameter, (str, int)):
            return str(parameter)

    def get_value_hashes(self) -> List[str]:
        return [self._left.get_hash(), self._right.get_hash()]

    def get_parameters(self) -> List[EqualParameter]:
        params = []
        if isinstance(self._left, EqualParameter):
            params.append(self._left)
        if isinstance(self._right, EqualParameter):
            params.append(self._right)
        return params

    def __eq__(self, __o: object) -> bool:
        return self._left == __o._left and self._right == __o._right

    def __hash__(self):
        return hash(self.hash)
