"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class SubnetId(FormatKeyword):
    id = "E1154"
    shortdesc = "Validate VPC subnet id format"
    description = "Check that a VPC subnet id matches a pattern"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::EC2::Subnet.Id"

    def __init__(self):
        super().__init__(
            format="AWS::EC2::Subnet.Id",
            pattern=r"^subnet-(([0-9A-Fa-f]{8})|([0-9A-Fa-f]{17}))$",
        )
