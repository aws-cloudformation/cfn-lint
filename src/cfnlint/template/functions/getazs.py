import json
from typing import Any, Iterable, Optional

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.template.functions._protocols import Fns
from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import Fn


class FnGetAZs(Fn):
    _type = "Fn::GetAZs"

    def __init__(self, instance: Any) -> None:
        super().__init__(instance)
        self._region: Optional[str] = None
        self._ref: Optional[int] = None

        if isinstance(instance, str):
            self._region = instance
            return
        if isinstance(instance, dict):
            if len(instance) == 1:
                if "Ref" in instance:
                    self._ref = hash(json.dumps(instance))
                    return

    @property
    def is_valid(self) -> bool:
        return self._ref is not None or self._region is not None

    def get_value(self, fns: Fns, region: str) -> Iterable[Any]:
        if not self.is_valid:
            raise Unpredictable(f"Fn::GetAZs is not valid {self._instance!r}")
        if self._region:
            try:
                yield AVAILABILITY_ZONES.get(region)
                return
            except KeyError:
                raise Unpredictable(f"Fn::GetAZs got unknown region: {region!r}")

        # we are either valid, _region or _ref
        if self._ref:
            for v in fns.get_value_by_hash(self._ref, region):
                try:
                    print(AVAILABILITY_ZONES)
                    yield AVAILABILITY_ZONES.get(v)
                except (TypeError, ValueError, KeyError):
                    raise Unpredictable(f"Fn::GetAZs got bad value: {v!r}")
            return
