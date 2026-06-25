"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from cfnlint.helpers import is_function

# Globals section key -> resource type
_GLOBALS_TYPE_MAP: dict[str, str] = {
    "Function": "AWS::Serverless::Function",
    "Api": "AWS::Serverless::Api",
    "HttpApi": "AWS::Serverless::HttpApi",
    "SimpleTable": "AWS::Serverless::SimpleTable",
    "StateMachine": "AWS::Serverless::StateMachine",
    "LayerVersion": "AWS::Serverless::LayerVersion",
    "CapacityProvider": "AWS::Serverless::CapacityProvider",
    "WebSocketApi": "AWS::Serverless::WebSocketApi",
}


def _is_intrinsic(value: Any) -> bool:
    k, _ = is_function(value)
    return k is not None


def _merge(global_value: Any, local_value: Any) -> Any:
    """Merge a global value with a local value.

    Rules (matching SAM translator behavior):
    - Primitives/intrinsics: local wins
    - Dicts: recursive merge, local keys override
    - Lists: concatenate global + local
    - Type mismatch: local wins
    """
    if isinstance(global_value, dict) and isinstance(local_value, dict):
        if _is_intrinsic(global_value) or _is_intrinsic(local_value):
            return local_value
        result = global_value.copy()
        for k, v in local_value.items():
            result[k] = _merge(result[k], v) if k in result else v
        return result

    if isinstance(global_value, list) and isinstance(local_value, list):
        return global_value + local_value

    return local_value


def merge_globals(template: dict[str, Any]) -> dict[str, Any]:
    """Merge Globals properties into SAM resources.

    Modifies the template in place and returns it.
    Does nothing if there is no Globals section.
    """
    globals_section = template.get("Globals")
    if not isinstance(globals_section, dict):
        return template

    resources = template.get("Resources")
    if not isinstance(resources, dict):
        return template

    # Build a map of resource_type -> global properties
    globals_by_type: dict[str, dict[str, Any]] = {}
    for section_name, props in globals_section.items():
        resource_type = _GLOBALS_TYPE_MAP.get(section_name)
        if resource_type and isinstance(props, dict):
            globals_by_type[resource_type] = props

    # Merge into each matching resource
    for resource in resources.values():
        if not isinstance(resource, dict):
            continue
        resource_type = resource.get("Type")
        if resource_type not in globals_by_type:
            continue

        # Support IgnoreGlobals attribute
        ignore = resource.get("IgnoreGlobals")
        if ignore == "*":
            continue

        global_props = deepcopy(globals_by_type[resource_type])

        if isinstance(ignore, list):
            for key in ignore:
                global_props.pop(key, None)

        local_props = resource.get("Properties")
        if not isinstance(local_props, dict):
            local_props = {}

        resource["Properties"] = _merge(global_props, local_props)

    return template
