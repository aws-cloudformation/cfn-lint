import json
from typing import Any, Iterable, Optional

from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import FnArray, Value


class FnSplit(FnArray):
    _supported_functions = [
        "Fn::Base64",
        "Fn::FindInMap",
        "Fn::GetAZs",
        "Fn::GetAtt",
        "Fn::If",
        "Fn::ImportValue",
        "Fn::Join",
        "Fn::Select",
        "Fn::Sub",
        "Ref",
        "Fn::ToJsonString",
    ]

    def __init__(self, instance: Any) -> None:
        self._length = 2
        super().__init__(
            instance,
            self._length,
            value_validators=[
                self._get_delimiter,
                self._get_source,
            ],
        )

    def _get_delimiter(self, instance: Any) -> Optional[Value]:
        if not isinstance(instance, str):
            return None

        return Value(_value=instance)

    def _get_source(self, instance: Any) -> Optional[Value]:
        if isinstance(instance, str):
            return Value(_value=instance)
        if isinstance(instance, dict):
            if len(instance) == 1:
                for k in instance.keys():
                    if k in self._supported_functions:
                        return Value(_fn=hash(json.dumps(instance)))
        return None

    def get_value(self, fns, region: str) -> Iterable[Any]:
        if not self.is_valid:
            raise Unpredictable(f"Fn::Split is not valid {self._instance!r}")

        success_ct = 0
        for delimiter in self.items[0].values(fns, region):
            for source in self.items[1].values(fns, region):
                if isinstance(source, str):
                    yield source.split(delimiter)
                    success_ct += 1
        if success_ct > 0:
            return
        raise Unpredictable(f"Fn::Split cannot be resolved {self._instance!r}")
