"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ecs_service
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ServiceFargate(CfnLintJsonSchema):
    id = "E3054"
    shortdesc = (
        "Validate ECS service using Fargate uses TaskDefinition that allows Fargate"
    )
    description = (
        "When using an ECS service with 'LaunchType' of 'FARGATE' "
        "the associated task definition must have 'RequiresCompatibilities' "
        "specified with 'FARGATE' listed"
    )
    tags = ["resources", "ecs"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::Service/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_service,
                filename="service_fargate.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        if err.validator == "required":
            return "'RequiresCompatibilities' is a required property"
        if err.validator == "contains":
            value = err.instance
            return f"{value!r} does not contain items matching 'FARGATE'"
        return err.message

    def _clean_error(self, err: ValidationError):
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
