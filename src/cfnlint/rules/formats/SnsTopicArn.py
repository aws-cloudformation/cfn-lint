"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class SnsTopicArn(FormatKeyword):
    id = "E1158"
    shortdesc = "Validate SNS topic ARN format"
    description = "Validate SNS topic ARN format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::SNS::Topic.Arn"

    def __init__(self):
        super().__init__(
            format="AWS::SNS::Topic.Arn",
            pattern=self.ARN_PREFIX + r"sns:[a-z0-9-]+:\d{12}:.+$",
        )
