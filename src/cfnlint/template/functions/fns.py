import json
from typing import Any, Dict, Iterable

from cfnlint.helpers import FUNCTIONS, ToPy
from cfnlint.template import functions
from cfnlint.template.functions._protocols import Fn
from cfnlint.template.functions.exceptions import Unpredictable


class Fns:
    def __init__(self, template: Any) -> None:
        self.functions: Dict[int, Fn] = {}
        for fn in list(set(FUNCTIONS) - set(["Fn::Contains"])):
            fn_py = ToPy(fn)
            cls = getattr(functions, fn_py.py_class)
            f_fns = template.search_deep_keys(fn_py.name)

            for f_fn in f_fns:
                c = cls(f_fn[-1])
                self.functions[c._hash] = c

    def get_value_by_hash(self, hash_: int, region: str) -> Iterable[Any]:
        if hash_ in self.functions:
            yield from self.functions[hash_].get_value(self, region)
            return
        raise Unpredictable("Unknown hash {hash!r}")

    def get_value(self, instance: Any, region: str) -> Iterable[Any]:
        _hash = hash(json.dumps(instance))
        yield from self.get_value_by_hash(_hash, region)
