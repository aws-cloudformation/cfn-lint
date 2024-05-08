"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_cloudwatch_alarm
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class AlarmAwsNamespacePeriod(CfnLintJsonSchema):
    id = "E3615"
    shortdesc = "Validate CloudWatch Alarm using AWS metrics has a correct period"
    description = (
        "Period < 60 not supported for namespaces with the following prefix: AWS/"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::CloudWatch::Alarm/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_cloudwatch_alarm,
                filename="aws_namespace_period.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
