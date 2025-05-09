"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParameterSet:

    source: str | None = field(default=None)
    parameters: dict[str, Any] = field(default_factory=dict)
