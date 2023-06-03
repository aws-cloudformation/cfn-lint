"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class AlarmAwsNamespacePeriod(BaseCfnSchema):
    id = "E3615"
    shortdesc = "Validate CloudWatch Alarm using AWS metrics has a correct period"
    description = (
        "Period < 60 not supported for namespaces with the following prefix: AWS/"
    )
    tags = ["resources"]
    schema_path = "aws_cloudwatch_alarm/aws_namespace_period"
