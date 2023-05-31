"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any, Iterable

# for python 3.7 support can be removed when we
# drop support
from typing_extensions import Protocol


class Fns(Protocol):
    def __init__(self, template: Any) -> None:
        ...  # pragma: no cover

    def get_value_by_hash(self, hash_: int, region: str) -> Iterable[Any]:
        ...  # pragma: no cover

    def get_value(self, instance: Any, region: str) -> Iterable[Any]:
        ...  # pragma: no cover


class Fn(Protocol):
    def __init__(self, instance: Any, template: Any) -> None:
        ...  # pragma: no cover

    def get_value(self, fns: Fns, region: str) -> Iterable[Any]:
        ...  # pragma: no cover
