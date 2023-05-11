"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class AlarmStatisticExclusive(BaseCfnSchema):
    id = "E3616"
    shortdesc = "Validate CloudWatch alarm doesn't use 'Stastic' and 'ExtendedStatistic' together"
    description = "When you specify 'Statistic' do not specify 'ExtendedStatistic'"
    tags = ["resources"]
    schema_path = "aws_cloudwatch_alarm/statistic_exclusive"
