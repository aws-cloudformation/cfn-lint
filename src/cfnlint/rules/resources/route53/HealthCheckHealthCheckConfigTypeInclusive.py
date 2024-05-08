"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.extensions.aws_route53_healthcheck
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class HealthCheckHealthCheckConfigTypeInclusive(CfnLintJsonSchema):
    id = "E3661"
    shortdesc = (
        "Validate Route53 health check has AlarmIdentifier when using CloudWatch"
    )
    description = (
        "When 'Type' is 'CLOUDWATCH_METRIC' you must specify 'AlarmIdentifier'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Route53::HealthCheck/Properties/HealthCheckConfig"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_route53_healthcheck,
                filename="healthcheckconfig_type_inclusive.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
