"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class AlarmMetricOnlyOne(BaseCfnSchema):
    id = "E3614"
    shortdesc = "Validate CloudWatch alarm metric only has 'MetricName' or 'Metrics'"
    description = "Specify only 'MetricName' or 'Metrics'"
    tags = ["resources"]
    schema_path = "aws_cloudwatch_alarm/metric_onlyone"
