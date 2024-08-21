"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

# Translate cfn-lint unique keywords into json schema keywords
import logging
from collections import deque
from typing import Any, Iterator

from cfnlint.schema import PROVIDER_SCHEMA_MANAGER

logger = logging.getLogger(__name__)


def required_xor(properties: list[str]) -> dict[str, list[Any]]:

    return {"oneOf": [{"required": [p]} for p in properties]}


def dependent_excluded(properties: dict[str, list[str]]) -> dict[str, list[Any]]:
    dependencies: dict[str, Any] = {"dependencies": {}}
    for prop, exclusions in properties.items():
        dependencies["dependencies"][prop] = {"not": {"anyOf": []}}
        for exclusion in exclusions:
            dependencies["dependencies"][prop]["not"]["anyOf"].append(
                {"required": exclusion}
            )

    return dependencies


_keywords = {
    "requiredXor": required_xor,
    "dependentExcluded": dependent_excluded,
}


def _find_keywords(schema: Any) -> Iterator[deque[str | int]]:

    if isinstance(schema, list):
        for i, item in enumerate(schema):
            for path in _find_keywords(item):
                path.appendleft(i)
                yield path
    elif isinstance(schema, dict):
        for key, value in schema.items():
            if key in _keywords:
                yield deque([key, value])
            else:
                for path in _find_keywords(value):
                    path.appendleft(key)
                    yield path


def translator(resource_type: str, region: str):
    keywords = list(
        _find_keywords(
            PROVIDER_SCHEMA_MANAGER.get_resource_schema(
                region=region, resource_type=resource_type
            ).schema
        )
    )

    for keyword in keywords:
        value = keyword.pop()
        key = keyword.pop()
        if not keyword:
            path = ""
        else:
            path = f"/{'/'.join(str(k) for k in keyword)}"

        patch = [
            {
                "op": "add",
                "path": f"{path}/allOf",
                "value": [],
            }
        ]

        logger.info(f"Patch {resource_type} add allOf for {key}")
        PROVIDER_SCHEMA_MANAGER._schemas[region][resource_type].patch(patches=patch)

        patch = [
            {
                "op": "remove",
                "path": f"{path}/{key}",
            },
            {"op": "add", "path": f"{path}/allOf/-", "value": _keywords[key](value)},  # type: ignore
        ]

        logger.info(f"Patch {resource_type} replace for {key}")
        PROVIDER_SCHEMA_MANAGER._schemas[region][resource_type].patch(patches=patch)
