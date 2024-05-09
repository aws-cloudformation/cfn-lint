"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Sequence

import cfnlint.data.schemas.extensions.aws_ecs_taskdefinition
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class LogConfiguration(CfnLintJsonSchema):
    id = "E3046"
    shortdesc = "Validate ECS task logging configuration for awslogs"
    description = (
        "When 'awslogs' the options 'awslogs-group' and 'awslogs-region' are required"
    )
    tags = ["resources"]

    def __init__(
        self, keywords: Sequence[str] | None = None, all_matches: bool = False
    ) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions/*/LogConfiguration"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_taskdefinition,
                filename="logging_configuration.json",
            ),
            all_matches=True,
        )
