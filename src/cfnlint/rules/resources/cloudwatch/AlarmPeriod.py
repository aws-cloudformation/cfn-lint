"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_cloudwatch_alarm
from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class AlarmPeriod(CfnLintJsonSchema):
    id = "E3615"
    shortdesc = "Validate the period is a valid value"
    description = "Valid values are 10, 30, 60, and any multiple of 60."
    tags = ["resources", "cloudwatch"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::CloudWatch::Alarm/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_cloudwatch_alarm,
                filename="period.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return f"{err.instance!r} is not one of [10, 30, 60] or a multiple of 60"
