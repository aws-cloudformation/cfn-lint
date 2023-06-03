"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any, Iterable, Optional

# for python 3.7 support can be removed when we
# drop support
from typing_extensions import Protocol


class Fns(Protocol):
    def __init__(self, template: Any) -> None:
        ...  # pragma: no cover

    def get_value(self, instance: Any, region: str) -> Iterable[Any]:
        ...  # pragma: no cover

    def get(self, key: Any) -> Optional["Fn"]:
        ...  # pragma: no cover":

    def __getitem__(self, key: Any) -> "Fn":
        ...  # pragma: no cover

    def __contains__(self, x: object) -> bool:
        ...  # pragma: no cover


class Fn(Protocol):
    def __init__(self, instance: Any, template: Any) -> None:
        ...  # pragma: no cover

    def get_value(self, fns: Fns, region: str) -> Iterable[Any]:
        ...  # pragma: no cover
