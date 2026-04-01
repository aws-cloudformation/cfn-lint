"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class AcmCertificateArn(FormatKeyword):
    id = "E1159"
    shortdesc = "Validate ACM certificate ARN format"
    description = "Validate ACM certificate ARN format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::ACM::Certificate.Arn"

    def __init__(self):
        super().__init__(
            format="AWS::ACM::Certificate.Arn",
            pattern=self.ARN_PREFIX + r"acm:[a-z0-9-]+:\d{12}:certificate/.+$",
        )
