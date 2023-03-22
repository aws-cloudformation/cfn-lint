import json
import logging
from typing import Any, Dict, List, Union

from cfnlint.conditions._utils import get_hash

LOGGER = logging.getLogger(__name__)


class EqualParameter:
    hash: str = ""

    def __init__(self, value: dict):
        self._value = value
        self.hash: str = get_hash(value)

    def __eq__(self, __o: Any):
        return self.hash == __o.hash


class Equal:
    hash: str
    _left: Union[EqualParameter, str]
    _right: Union[EqualParameter, str]
    _is_static: Union[bool, None]

    def __init__(self, equal: List[Union[str, dict]]) -> None:
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
                self._is_static = self._left == self._right
            return
        raise ValueError("Equals has to be a list of two values")

    def _init_parameter(
        self, parameter: Union[Dict, str]
    ) -> Union[EqualParameter, str]:
        if isinstance(parameter, dict):
            return EqualParameter(parameter)
        return str(parameter)

    def is_static(self) -> Union[bool, None]:
        """Returns a boolean value if the result is always True or False or None if
            it isn't a static boolean

        Args: None

        Returns:
            Union[bool, None]: None if the equals can be True or False or True/False if
            the equals will always return the same result
        """
        return self._is_static

    def get_parameters(self) -> List[EqualParameter]:
        """Returns a List of the EqualParameter that make up the Condition

        Args: None

        Returns:
            List[Equal]: A list of the left and right equal parameters if they are
                         of type EqualParameter
        """
        params = []
        if isinstance(self._left, EqualParameter):
            params.append(self._left)
        if isinstance(self._right, EqualParameter):
            params.append(self._right)
        return params

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right
