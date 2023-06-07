"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, List, Optional

from cfnlint.template.functions._protocols import Fns
from cfnlint.template.functions._utils import add_to_lists
from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import FnArray, Value


@dataclass
class _JoinSource(Value):
    def values(self, fns: Fns, region: str) -> Iterator[Any]:
        if self._fn is not None:
            if self._fn not in fns:
                raise Unpredictable(f"{self._fn!r} not in functions list")
            yield from fns.get(self._fn).get_value(fns, region)  # type: ignore
        else:
            lists: List[List[str]] = []
            for item in self._value:
                n_items = list(item.values(fns, region))
                lists = add_to_lists(
                    lists, n_items, (str, int, float), lambda x: str(x)
                )
            yield from iter(lists)

    def add(self, Value):
        self._value.append(Value)


class FnJoin(FnArray):
    _multiple_functions = [
        "Fn::Cidr",
        "Fn::FindInMap",
        "Fn::GetAZs",
        "Fn::If",
        "Fn::Select",
        "Fn::Split",
        "Ref",
    ]

    _singular_functions = [
        "Fn::Base64",
        "Fn::FindInMap",
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
        if isinstance(instance, dict):
            if len(instance) == 1:
                for k in instance.keys():
                    if k in self._multiple_functions:
                        return _JoinSource(_fn=hash(json.dumps(instance)))

        if isinstance(instance, list):
            join_source = _JoinSource(_value=[])
            for item in instance:
                if isinstance(item, (str, int, float)):
                    join_source.add(Value(_value=item))
                elif isinstance(item, dict):
                    if len(item) != 1:
                        return None
                    for k in item.keys():
                        if k in self._singular_functions:
                            join_source.add(Value(_fn=hash(json.dumps(item))))
                        else:
                            return None
                else:
                    return None
            return join_source
        return None

    def get_value(self, fns, region: str) -> Iterable[Any]:
        if not self.is_valid:
            raise Unpredictable(f"Fn::Join is not valid {self._instance!r}")

        success_ct = 0
        for delimiter in self.items[0].values(fns, region):
            for source in self.items[1].values(fns, region):
                if isinstance(source, list):
                    yield delimiter.join(source)
                    success_ct += 1
        if success_ct > 0:
            return
        raise Unpredictable(f"Fn::Join cannot be resolved {self._instance!r}")
