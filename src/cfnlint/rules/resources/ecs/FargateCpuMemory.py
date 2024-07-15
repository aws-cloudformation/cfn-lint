"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ecs_taskdefinition
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FargateCpuMemory(CfnLintJsonSchema):
    id = "E3047"
    shortdesc = (
        "Validate ECS Fargate tasks have the right combination of CPU and memory"
    )
    description = (
        "When using a ECS Fargate task there is a specfic combination "
        "of memory and cpu that can be used"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-memory"
    tags = ["properties", "ecs", "service", "container", "fargate"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::TaskDefinition/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_taskdefinition,
                filename="fargate_cpu_memory.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            f"Cpu {instance.get('Cpu')!r} is not "
            "compatible with memory "
            f"{instance.get('Memory')!r}"
        )
