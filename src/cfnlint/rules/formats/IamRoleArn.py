"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class IamRoleArn(FormatKeyword):
    id = "E1156"
    shortdesc = "Validate IAM role ARN format"
    description = "Validate IAM role ARN validation for ref/gett and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::IAM::Role.Arn"

    def __init__(self):
        super().__init__(
            format="AWS::IAM::Role.Arn",
            pattern=r"^arn:(aws|aws-cn|aws-iso|aws-iso-[a-z]{1}|aws-us-gov):iam::\d{12}:role/.*$",
        )
