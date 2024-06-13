"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import Any, List


@dataclass
class Conditions:
    # Template level parameters
    conditions: InitVar[dict[str, Any] | None]
    _transforms: List[str] = field(init=False, default_factory=list)

    def __post_init__(self, transforms) -> None:
        if transforms is None:
            return
        if not isinstance(transforms, list):
            transforms = [transforms]

        for transform in transforms:
            if not isinstance(transform, str):
                raise ValueError("Transform must be a string")
            self._transforms.append(transform)
