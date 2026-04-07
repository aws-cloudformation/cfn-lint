"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class S3BucketName(FormatKeyword):
    id = "E1161"
    shortdesc = "Validate S3 bucket name format"
    description = "Validate S3 bucket name format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::S3::Bucket.Name"

    def __init__(self):
        super().__init__(
            format="AWS::S3::Bucket.Name",
            pattern=r"^(?![.\-])(?!.*\.\.)(?!.*\-\.)(?!.*\.\-)[a-z0-9.\-]{3,63}(?<![.\-])$",
        )
