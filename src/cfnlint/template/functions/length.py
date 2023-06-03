from typing import Any

from cfnlint.template.functions.fn import Fn


class FnLength(Fn):
    def __init__(self, instance: Any) -> None:
        super().__init__(instance)
