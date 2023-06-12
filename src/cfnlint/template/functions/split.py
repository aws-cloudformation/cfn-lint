"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from collections import deque
from typing import Any, Iterable, Optional

from cfnlint.context.value import Value, ValueType
from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import FnArray, FnValue


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

    def __init__(self, instance: Any, template: Any = None) -> None:
        self._length = 2
        super().__init__(
            instance,
            self._length,
            value_validators=[
                self._get_delimiter,
                self._get_source,
            ],
        )

    def _get_delimiter(self, instance: Any) -> Optional[FnValue]:
        if not isinstance(instance, str):
            return None

        return FnValue(_value=instance)

    def _get_source(self, instance: Any) -> Optional[FnValue]:
        if isinstance(instance, str):
            return FnValue(_value=instance)
        if isinstance(instance, dict):
            if len(instance) == 1:
                for k in instance.keys():
                    if k in self._supported_functions:
                        return FnValue(_fn=hash(json.dumps(instance)))
        return None

    def get_value(self, fns, region: str) -> Iterable[Value]:
        if not self.is_valid:
            raise Unpredictable(f"Fn::Split is not valid {self._instance!r}")

        success_ct = 0
        for delimiter in self.items[0].values(fns, region):
            for source in self.items[1].values(fns, region):
                if isinstance(source, str):
                    yield Value(
                        value=source.split(delimiter),
                        value_type=ValueType.FUNCTION,
                        path=deque([]),
                    )
                    success_ct += 1
        if success_ct > 0:
            return
        raise Unpredictable(f"Fn::Split cannot be resolved {self._instance!r}")
