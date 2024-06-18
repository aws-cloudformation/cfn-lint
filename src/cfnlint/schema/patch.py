"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class SchemaPatch:
    included_resource_types: list[str]
    excluded_resource_types: list[str]
    patches: dict[str, list[Dict]]

    @staticmethod
    def from_dict(value: Dict):
        return SchemaPatch(
            included_resource_types=value.get("IncludeResourceTypes", []),
            excluded_resource_types=value.get("ExcludeResourceTypes", []),
            patches=value.get("Patches", {}),
        )
