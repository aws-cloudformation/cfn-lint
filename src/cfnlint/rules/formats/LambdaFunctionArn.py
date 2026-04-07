"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class LambdaFunctionArn(FormatKeyword):
    id = "E1160"
    shortdesc = "Validate Lambda function ARN format"
    description = "Validate Lambda function ARN format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::Lambda::Function.Arn"

    def __init__(self):
        super().__init__(
            format="AWS::Lambda::Function.Arn",
            pattern=self.ARN_PREFIX + r"lambda:[a-z0-9-]+:\d{12}:function:.+(:.+)?$",
        )
