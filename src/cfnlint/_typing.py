"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Protocol, Union

if TYPE_CHECKING:
    from cfnlint.rules._Rule import RuleMatch

Path = List[Union[str, int]]


class CheckValueFn(Protocol):
    def __call__(self, value: Any, path: Path, **kwargs: Any) -> list[RuleMatch]: ...
