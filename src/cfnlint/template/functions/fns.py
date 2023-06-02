from __future__ import annotations

import json
from collections import UserDict
from typing import TYPE_CHECKING, Any, Dict

from cfnlint.helpers import FUNCTIONS, ToPy
from cfnlint.template import functions
from cfnlint.template.functions._protocols import Fn
from cfnlint.template.functions.exceptions import Unpredictable

if TYPE_CHECKING:
    FnsParent = UserDict[int, Fn]
else:
    FnsParent = UserDict


class Fns(FnsParent):
    def __init__(self, template: Any = None) -> None:
        super().__init__()
        if template is None:
            return
        for fn in list(set(FUNCTIONS) - set(["Fn::Contains"])):
            fn_py = ToPy(fn)
            cls = getattr(functions, fn_py.py_class)
            f_fns = template.search_deep_keys(fn_py.name)

            for f_fn in f_fns:
                c = cls(f_fn[-1])
                self[{fn: f_fn[-1]}] = c

    def __getitem__(self, key: Any) -> Fn:
        try:
            if key in self.data:
                return super().__getitem__(key)  # type: ignore
        except TypeError:
            pass
        _hash = hash(json.dumps(key))
        if _hash in self.data:
            return super().__getitem__(_hash)  # type: ignore
        raise Unpredictable(f"Unable to find function {key}")

    def get_value(self, instance: Any, region: str):
        return self[instance].get_value(self, region)

    def __setitem__(self, key: Dict[str, Any], item: Fn) -> None:  # type: ignore
        return super().__setitem__(hash(json.dumps(key)), item)
