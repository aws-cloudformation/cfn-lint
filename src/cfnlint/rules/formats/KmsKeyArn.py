"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class KmsKeyArn(FormatKeyword):
    id = "E1157"
    shortdesc = "Validate KMS key ARN format"
    description = "Validate KMS key ARN format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::KMS::Key.Arn"

    def __init__(self):
        super().__init__(
            format="AWS::KMS::Key.Arn",
            pattern=self.ARN_PREFIX + r"kms:[a-z0-9-]+:\d{12}:(key|alias)/.+$",
        )
