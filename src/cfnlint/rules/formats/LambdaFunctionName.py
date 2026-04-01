"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class LambdaFunctionName(FormatKeyword):
    id = "E1163"
    shortdesc = "Validate Lambda function name format"
    description = (
        "Validate Lambda function name format for ref/getatt and string values"
    )
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::Lambda::Function.Name"

    def __init__(self):
        super().__init__(
            format="AWS::Lambda::Function.Name",
            pattern=r"^[a-zA-Z0-9_-]{1,140}$",
        )
