"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class AlarmAwsNamespacePeriod(CfnLintJsonSchema):
    id = "E3615"
    shortdesc = "Validate CloudWatch Alarm using AWS metrics has a correct period"
    description = (
        "Period < 60 not supported for namespaces with the following prefix: AWS/"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(keywords=["aws_cloudwatch_alarm/aws_namespace_period"])
