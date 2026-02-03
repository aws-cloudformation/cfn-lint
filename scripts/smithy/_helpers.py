"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from pathlib import Path

from cfnlint.schema.resolver import RefResolver


def load_schema_file(schema_file: Path) -> RefResolver:
    """Load a CloudFormation resource schema file"""
    with open(schema_file, "r") as f:
        schema = json.load(f)

    return RefResolver.from_schema(schema)
