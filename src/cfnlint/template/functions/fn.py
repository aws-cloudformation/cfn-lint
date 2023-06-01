import json
from typing import Any, Callable, Dict, Iterable, Optional

from cfnlint.template.functions._protocols import Fns
from cfnlint.template.functions.exceptions import Unpredictable


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
        value_validators: Dict[int, Callable[[], bool]],
        template: Any = None,
    ) -> None:
        super().__init__(instance, template)

        if not isinstance(instance, list):
            return

        if len(instance) != length:
            return
