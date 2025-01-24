"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class SecurityGroupId(FormatKeyword):
    id = "E1150"
    shortdesc = "Validate security group format"
    description = (
        "Security groups have to ref/gettatt to a security "
        "group or has the valid pattern"
    )
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::EC2::SecurityGroup.Id"

    def __init__(self):
        super().__init__(
            format="AWS::EC2::SecurityGroup.Id",
            pattern=r"^sg-([a-fA-F0-9]{8}|[a-fA-F0-9]{17})$",
        )
