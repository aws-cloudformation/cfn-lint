"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from pathlib import Path

from cfnlint.schema.resolver import RefResolver


def load_schema_file(schema_path: Path) -> RefResolver:
    with open(schema_path, "r") as f:
        data = json.load(f)
        return RefResolver.from_schema(data)
