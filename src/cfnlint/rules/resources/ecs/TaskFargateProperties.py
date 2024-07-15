"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

import cfnlint.data.schemas.extensions.aws_ecs_taskdefinition
from cfnlint.jsonschema import ValidationResult
from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class TaskFargateProperties(CfnLintJsonSchema):
    id = "E3048"
    shortdesc = "Validate ECS Fargate tasks have required properties and values"
    description = (
        "When using a ECS Fargate task there is a specfic combination "
        "of required properties and values"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-memory"
    tags = ["properties", "ecs", "service", "container", "fargate"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::TaskDefinition/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_taskdefinition,
                filename="fargate_properties.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for err in super().validate(validator, keywords, instance, schema):
            if err.validator == "not":
                err.message = "'PlacementConstraints' isn't supported for Fargate tasks"
                err.path = deque(["PlacementConstraints"])
                yield err
                continue
            yield err
