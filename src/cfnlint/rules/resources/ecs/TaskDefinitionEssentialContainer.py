"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ecs_taskdefinition
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class TaskDefinitionEssentialContainer(CfnLintJsonSchema):
    """
    Check ECS TaskDefinition ContainerDefinitions Property
    Specifies at least one Essential Container
    """

    id = "E3042"
    shortdesc = "Validate at least one essential container is specified"
    description = (
        "Check that every TaskDefinition specifies at least one essential container"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-essential"
    tags = ["properties", "ecs", "task", "container", "fargate"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions/*"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_taskdefinition,
                filename="containerdefinitions_essential.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "At least one essential container is required"
