"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Sequence

from cfnlint.context import Path
from cfnlint.context.conditions import Unsatisfiable
from cfnlint.jsonschema import Validator


def get_resource_by_name(
    validator: Validator, name: str, types: Sequence[str] | None = None
) -> tuple[Any, Validator]:

    resource = validator.context.resources.get(name)
    if not resource:
        return None, validator

    if types and resource.type not in types:
        return None, validator

    if resource.condition:
        try:
            validator = validator.evolve(
                context=validator.context.evolve(
                    conditions=validator.context.conditions.evolve(
                        {
                            resource.condition: True,
                        }
                    ),
                )
            )
        except Unsatisfiable:
            return None, validator

    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque(["Resources", name]),
                cfn_path=deque(["Resources", resource.type]),
            )
        )
    )

    return validator.cfn.template.get("Resources", {}).get(name), validator
