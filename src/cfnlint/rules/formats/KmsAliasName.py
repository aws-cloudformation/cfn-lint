"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class KmsAliasName(FormatKeyword):
    id = "E1164"
    shortdesc = "Validate KMS alias name format"
    description = "Validate KMS alias name format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::KMS::Alias.AliasName"

    def __init__(self):
        super().__init__(
            format="AWS::KMS::Alias.AliasName",
            pattern=r"^alias/[a-zA-Z0-9:/_-]+$",
        )
