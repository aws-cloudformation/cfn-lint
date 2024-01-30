"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


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
            keywords=["aws_route53_healthcheck/healthcheckconfig_type_inclusive"]
        )
