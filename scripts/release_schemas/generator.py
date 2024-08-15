#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from collections import deque
from pathlib import Path

import _translator

from cfnlint.helpers import REGIONS, ToPy, format_json_string, load_plugins
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _get_schema_path(schema, path):
    s = schema.schema
    schema_path = deque([])
    while path:
        key = path.popleft()
        if key == "*":
            schema_path.append("items")
            s = s["items"]
        else:
            s = s["properties"][key]
            schema_path.extend(["properties", key])

        pointer = s.get("$ref")
        if pointer:
            _, s = schema.resolver.resolve(pointer)
            schema_path = deque(pointer.split("/")[1:])

    return schema_path


def _build_patch(path, patch):
    if not path:
        path_str = "/allOf"
    else:
        path_str = f"/{'/'.join(path)}/allOf"

    return (
        [
            {
                "op": "add",
                "path": path_str,
                "value": [],
            }
        ],
        [
            {
                "op": "add",
                "path": f"{path_str}/-",
                "value": patch,
            }
        ],
    )


schemas = {}

##########################
#
# Build the definitive list of all resource types across all regions
#
###########################

for region in ["us-east-1"] + list((set(REGIONS) - set(["us-east-1"]))):
    for resource_type in PROVIDER_SCHEMA_MANAGER.get_resource_types(region):
        if resource_type in ["AWS::CDK::Metadata", "Module"]:
            continue
        if resource_type not in schemas:
            schemas[resource_type] = region


##########################
#
# Merge in rule schemas into the resource schemas
#
###########################

rules_folder = Path("src") / "cfnlint" / "rules"

rules = load_plugins(
    rules_folder,
    name="CfnLintJsonSchema",
    modules=(
        "cfnlint.rules.jsonschema.CfnLintJsonSchema",
        "cfnlint.rules.jsonschema.CfnLintJsonSchema.CfnLintJsonSchema",
    ),
)

for rule in rules:
    if rule.__class__.__base__ == (
        "cfnlint.rules.jsonschema."
        "CfnLintJsonSchemaRegional.CfnLintJsonSchemaRegional"
    ):
        continue
    if not rule.id or rule.schema == {}:
        continue

    for keyword in rule.keywords:
        if not keyword.startswith("Resources/"):
            continue
        path = deque(keyword.split("/"))

        if len(path) < 3:
            continue

        path.popleft()
        resource_type = path.popleft()
        resource_properties = path.popleft()
        if resource_type not in schemas and resource_properties != "Properties":
            continue

        schema_path = _get_schema_path(
            PROVIDER_SCHEMA_MANAGER.get_resource_schema(
                schemas[resource_type], resource_type
            ),
            path,
        )
        all_of_patch, schema_patch = _build_patch(schema_path, rule.schema)

        PROVIDER_SCHEMA_MANAGER._schemas[schemas[resource_type]][resource_type].patch(
            patches=all_of_patch
        )
        PROVIDER_SCHEMA_MANAGER._schemas[schemas[resource_type]][resource_type].patch(
            patches=schema_patch
        )

        logger.info(f"Patch {rule.id} for {resource_type} in {schemas[resource_type]}")


for resource_type, region in schemas.items():
    rt_py = ToPy(resource_type)

    _translator.translator(resource_type, region)

    with open(f"local/release_schemas/{rt_py.py}.json", "w") as f:
        f.write(
            format_json_string(
                PROVIDER_SCHEMA_MANAGER.get_resource_schema(
                    region, resource_type
                ).schema
            )
        )
