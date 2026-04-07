"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class KmsKeyId(FormatKeyword):
    id = "E1162"
    shortdesc = "Validate KMS key ID format"
    description = "Validate KMS key ID format for key UUIDs and aliases"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::KMS::Key.Id"

    def __init__(self):
        super().__init__(
            format="AWS::KMS::Key.Id",
            pattern=(
                r"^("
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
                r"|mrk-[0-9a-f]{32}"
                r"|alias/[a-zA-Z0-9/_-]+"
                r")$"
            ),
        )
