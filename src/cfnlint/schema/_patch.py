"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from typing import Dict, Sequence

from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER
from cfnlint.schema.other_schema_manager import OTHER_SCHEMA_MANAGER

LOGGER = logging.getLogger(__name__)


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
            LOGGER.error("Override spec file not found: %s", filename)
            sys.exit(1)
        elif e.errno == 21:
            LOGGER.error(
                "Override spec file references a directory, not a file: %s",
                filename,
            )
            sys.exit(1)
        elif e.errno == 13:
            LOGGER.error(
                "Permission denied when accessing override spec file: %s", filename
            )
            sys.exit(1)
    except ValueError as err:
        LOGGER.error("Override spec file %s is malformed: %s", filename, err)
        sys.exit(1)


def reset():
    PROVIDER_SCHEMA_MANAGER.reset()
    OTHER_SCHEMA_MANAGER.reset()
