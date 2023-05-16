from typing import Any, Iterable, Protocol


class Fns(Protocol):
    def __init__(self, template: Any) -> None:
        ...

    def get_value_by_hash(self, hash: str, region: str) -> Iterable[Any]:
        ...

    def get_value(self, instance: Any, region: str) -> Iterable[Any]:
        ...


class Fn(Protocol):
    def __init__(self, instance: Any, template: Any) -> None:
        ...

    def get_value(self, instance: Any, region: str) -> Iterable[Any]:
        ...
