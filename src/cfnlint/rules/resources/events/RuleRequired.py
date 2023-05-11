"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class RuleRequired(BaseCfnSchema):
    id = "E3649"
    shortdesc = "Validate Events has required properties"
    description = "Specify at least one of 'EventPattern' and 'ScheduleExpression'"
    tags = ["resources"]
    schema_path = "aws_events_rule/required"
