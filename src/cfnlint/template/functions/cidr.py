from typing import Any

from cfnlint.template.functions.fn import Fn


class FnCidr(Fn):
    def __init__(self, instance: Any) -> None:
        super().__init__(instance)
