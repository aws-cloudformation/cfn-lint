"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import TYPE_CHECKING, Any, List, Protocol, Union

if TYPE_CHECKING:
    from cfnlint.rules import RuleMatch

RuleMatches = List["RuleMatch"]
Path = List[Union[str, int]]


class CheckValueFn(Protocol):
    def __call__(self, value: Any, path: Path, **kwargs: Any) -> List["RuleMatch"]: ...
