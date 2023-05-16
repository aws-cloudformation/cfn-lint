import json
from typing import Any, Iterable

from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import Fn


class FnSplit(Fn):
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
        super().__init__(instance)
        if not isinstance(instance, list):
            return
        if len(instance) != 2:
            return

        instance = list(instance)
        self.delimiter = instance[0]
        if not isinstance(self.delimiter, str):
            return

        self._string = None
        source = instance[1]
        if isinstance(source, str):
            self._string = source
            self._is_valid = True
        if isinstance(source, dict):
            if len(source) == 1:
                for k, v in source.items():
                    if k in self._supported_functions:
                        self._fn = hash(json.dumps(source))
                        self._is_valid = True

    def get_value(self, fns, region: str) -> Iterable[Any]:
        if not self._is_valid:
            raise Unpredictable(f"Fn::Split is not valid {self._instance!r}")
        if self._string:
            yield self._string.split(self.delimiter)
            return

        if self._fn not in fns:
            raise Unpredictable(f"Fn::Split cannot be resolved {self._instance!r}")

        values = list(fns[self._fn].get_value(fns, region))
        success_ct = 0
        for value in values:
            if isinstance(value, str):
                yield value.split(self.delimiter)
                success_ct += 1
        if success_ct > 0:
            return
        raise Unpredictable(f"Fn::Split cannot be resolved {self._instance!r}")
