"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DeploymentFileData:

    template_file_path: str = field()
    parameters: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
