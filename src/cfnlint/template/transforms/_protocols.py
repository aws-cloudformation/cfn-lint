"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from typing_extensions import Protocol

from cfnlint.template.transforms._types import TransformResult


class Transformer(Protocol):
    def transform(self, cfn: Any) -> TransformResult:
        ...
