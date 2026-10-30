"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Sequence

from cfnlint.exceptions import SchemaPatchError
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER
from cfnlint.schema.other_schema_manager import OTHER_SCHEMA_MANAGER


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


def patch(filename: str, regions: Sequence[str]):
    try:
        with open(filename, encoding="utf-8") as fp:
            custom_spec_data = json.load(fp)
            schema_patch = SchemaPatch.from_dict(custom_spec_data)
            for region in regions:
                PROVIDER_SCHEMA_MANAGER.patch(schema_patch, region)

            OTHER_SCHEMA_MANAGER.patch(schema_patch, region)
    except IOError as e:
        if e.errno == 2:
            msg = f"Override spec file not found: {filename}"
        elif e.errno == 21:
            msg = f"Override spec file references a directory, not a file: {filename}"
        elif e.errno == 13:
            msg = f"Permission denied when accessing override spec file: {filename}"
        else:
            msg = f"Override spec file {filename} could not be read: {e}"
        raise SchemaPatchError(msg) from e
    except ValueError as err:
        raise SchemaPatchError(
            f"Override spec file {filename} is malformed: {err}"
        ) from err


def reset():
    PROVIDER_SCHEMA_MANAGER.reset()
    OTHER_SCHEMA_MANAGER.reset()
