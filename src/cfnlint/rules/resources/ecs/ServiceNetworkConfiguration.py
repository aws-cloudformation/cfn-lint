"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_ecs_service
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ServiceNetworkConfiguration(CfnLintJsonSchema):
    id = "E3052"
    shortdesc = "Validate ECS service requires NetworkConfiguration"
    description = (
        "When using an ECS task definition has NetworkMode set to "
        "'awsvpc' then 'NetworkConfiguration' is required"
    )
    tags = ["resources", "ecs"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::Service/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_service,
                filename="service_network_configuration.json",
            ),
            all_matches=True,
        )
