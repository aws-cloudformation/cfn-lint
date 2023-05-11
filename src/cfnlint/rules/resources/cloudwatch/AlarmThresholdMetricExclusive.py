"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class AlarmThresholdMetricExclusive(BaseCfnSchema):
    id = "E3612"
    shortdesc = "Validate CloudWatch alarm threshold doesn't also have ThresholdMetricId"
    description = "When you specify 'Threshold' do not specify 'ThresholdMetricId'"
    tags = ["resources"]
    schema_path = "aws_cloudwatch_alarm/thresholdmetric_exclusive"
