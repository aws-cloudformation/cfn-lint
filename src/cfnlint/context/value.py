"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValueType(Enum):
    STANDARD = 0
    FUNCTION = 1
    PSEUDO_PARAMETER = 2


@dataclass
class Value:
    value: Any = field(init=True)
    value_type: ValueType = field(init=True, default=ValueType.STANDARD)
    path: deque[str | int] = field(init=True, default_factory=deque)

    def __repr__(self):
        if self.value_type == ValueType.PSEUDO_PARAMETER:
            return f"{self.value!r} (pseudo parameter)"
        return f"{self.value!r} ({self.path})"
