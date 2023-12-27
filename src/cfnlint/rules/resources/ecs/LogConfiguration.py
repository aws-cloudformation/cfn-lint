"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class TableBillingModeExclusive(BaseCfnSchema):
    id = "E3046"
    shortdesc = "Validate ECS task logging configuration for awslogs"
    description = (
        "When 'awslogs' the options 'awslogs-group' and 'awslogs-region' are required"
    )
    tags = ["resources"]
    schema_path = "aws_ecs_taskdefinition/logging_configuration"
    all_matches = True
