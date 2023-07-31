"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Sequence


@dataclass
class Transforms:
    # Template level parameters
    transforms: Sequence[str] = field(init=True, default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.transforms, list):
            self.transforms = [self.transforms]

    def has_language_extensions_transform(self):
        lang_extensions_transform = "AWS::LanguageExtensions"
        return bool(lang_extensions_transform in self.transforms)
