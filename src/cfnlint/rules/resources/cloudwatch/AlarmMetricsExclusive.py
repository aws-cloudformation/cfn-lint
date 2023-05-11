"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class AlarmMetricsExclusive(BaseCfnSchema):
    id = "E3613"
    shortdesc = "Validate CloudWatch metrics alarm doesn't use Metrics " \
        "with other exclusive properties"
    description = "When you specify 'Metrics' do not specify 'Dimensions', 'Period', 'Namespace', 'Statistic', 'ExtendedStatistic', or 'Unit'"
    tags = ["resources"]
    schema_path = "aws_cloudwatch_alarm/metrics_exclusive"
