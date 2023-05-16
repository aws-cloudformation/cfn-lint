import json
from collections import namedtuple
from typing import Any, Iterable, List, Union

from cfnlint.template.functions._utils import add_to_lists
from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import Fn

_JoinItem = namedtuple("_JoinItem", ["string", "fn"])


class FnJoin(Fn):
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
        super().__init__(instance)
        if not isinstance(instance, list):
            return
        if len(instance) != 2:
            return

        instance = list(instance)
        self._delimiter: str = instance[0]
        if not isinstance(self._delimiter, str):
            return

        self._items: Union[List[_JoinItem], int] = []
        source = instance[1]
        if isinstance(source, list):
            for item in source:
                if isinstance(item, (str, int, float)):
                    self._items.append(_JoinItem(item, None))
                elif isinstance(item, dict):
                    if len(item) != 1:
                        break
                    for k, v in item.items():
                        if k in self._singular_functions:
                            self._items.append(
                                _JoinItem(None, hash(json.dumps({k: v})))
                            )
                            continue
                else:
                    break
            else:
                self._is_valid = True
        elif isinstance(source, dict):
            if len(source) == 1:
                for k, v in source.items():
                    if k in self._multiple_functions:
                        self._items = hash(json.dumps(source))
                        self._is_valid = True

    def get_value(self, fns, region: str) -> Iterable[Any]:
        if not self._is_valid:
            raise Unpredictable(f"Fn::Join is not valid {self._instance!r}")

        lists: List[List[str]] = [[]]
        if isinstance(self._items, int):
            if self._items not in fns:
                raise Unpredictable(f"Fn::Join cannot be resolved {self._instance!r}")
            for n_item in fns[self._items].get_value(fns, region):
                if not isinstance(n_item, (list)):
                    raise Unpredictable(
                        f"Fn::Join can only join lists {self._instance!r}"
                    )
                yield self._delimiter.join(n_item)
            return
        else:
            for item in self._items:
                if item.fn:
                    if item.fn not in fns:
                        raise Unpredictable(
                            f"Fn::Join cannot be resolved {self._instance!r}"
                        )
                    n_items = list(fns[item.fn].get_value(fns, region))
                    lists = add_to_lists(
                        lists, n_items, (str, int, float), lambda x: str(x)
                    )
                else:
                    lists = add_to_lists(
                        lists, [item.string], (str, int, float), lambda x: str(x)
                    )

        if len(lists) > 0:
            for l_item in lists:
                yield self._delimiter.join(l_item)
            return
        raise Unpredictable(f"Fn::Join cannot be resolved {self._instance!r}")
