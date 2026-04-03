"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ecs_service
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ServiceFargateLogDriver(CfnLintJsonSchema):
    id = "E3713"
    shortdesc = "Validate Fargate ECS services use supported log drivers"
    description = (
        "When using an ECS service with 'LaunchType' of 'FARGATE' "
        "the referenced task definition containers must use a supported "
        "log driver ('awslogs', 'splunk', or 'awsfirelens'). "
        "Other log drivers like 'json-file' or 'syslog' are not "
        "supported on Fargate."
    )
    source_url = (
        "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_awslogs.html"
    )
    tags = ["resources", "ecs"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::Service/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_service,
                filename="service_fargate_log_driver.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        if err.validator == "enum":
            return (
                f"{err.instance!r} is not a supported Fargate log driver. "
                f"Use 'awslogs', 'splunk', or 'awsfirelens'"
            )
        return err.message

    def _clean_error(self, err: ValidationError) -> ValidationError:
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
