import json
from typing import Any, Iterable, Optional

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import Fn
from cfnlint.template.functions.fns import Fns


class FnGetAZs(Fn):
    _type = "Fn::GetAZs"

    def __init__(self, instance: Any) -> None:
        super().__init__(instance)
        self._region: Optional[str] = None
        self._ref: Optional[int] = None

        if isinstance(instance, str):
            self._region = instance
            self._is_valid = True
            return
        if isinstance(instance, dict):
            if len(instance) == 1:
                if "Ref" in instance:
                    self._ref = hash(json.dumps(instance))
                    self._is_valid = True
                    return

    def get_value(self, fns: Fns, region: str) -> Iterable[Any]:
        if not self._is_valid:
            raise Unpredictable(f"Fn::GetAZs is not valid {self._instance!r}")
        if self._region:
            try:
                yield AVAILABILITY_ZONES.get(region)
                return
            except KeyError:
                raise Unpredictable(f"Fn::GetAZs got unknown region: {region!r}")
        if self._ref:
            for v in fns.get_value_by_hash(self._ref, region):
                try:
                    yield AVAILABILITY_ZONES.get(v)
                except (TypeError, ValueError, KeyError):
                    raise Unpredictable(f"Fn::GetAZs got bad value: {v!r}")
            return

        raise Unpredictable("Fn::GetAZs unknown error")
