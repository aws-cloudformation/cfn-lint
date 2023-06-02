from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Iterator, List, Optional

from cfnlint.template.functions._protocols import Fns
from cfnlint.template.functions.exceptions import Unpredictable


@dataclass
class Value:
    _value: Any = field(init=True, default=None)
    _fn: int | None = field(init=True, default=None)

    def values(self, fns: Fns, region: str) -> Iterator[Any]:
        if self._fn is not None:
            if self._fn not in fns:
                raise Unpredictable(f"{self._fn!r} not in functions list")
            yield from fns.get(self._fn).get_value(fns, region)  # type: ignore
        else:
            yield self._value


class Fn:
    _type: Optional[str] = None

    def __init__(self, instance: Any, template: Any = None) -> None:
        self._instance = instance
        self._hash = hash(json.dumps({self._type: self._instance}))

    def get_value(self, fns: Fns, region: str) -> Iterable[Any]:
        raise Unpredictable(self._instance)

    def __hash__(self) -> int:
        return self._hash

    @property
    def is_valid(self) -> bool:
        return False


class FnArray(Fn):
    def __init__(
        self,
        instance: Any,
        length: int,
        value_validators: List[Callable[[Any], Optional[Value]]],
        template: Any = None,
    ) -> None:
        super().__init__(instance, template)
        self.items: List[Value] = []
        self._length: int = length
        if not isinstance(instance, list):
            return

        if len(instance) != self._length:
            return

        for i, item in enumerate(instance):
            value = value_validators[i](item)
            if value is None:
                return
            self.items.append(value)

    @property
    def is_valid(self) -> bool:
        if not self.items:
            return False
        return len(self.items) == self._length
