"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class SecurityGroupName(FormatKeyword):
    id = "E1153"
    shortdesc = "Validate security group name"
    description = "Security group names have to valid pattern"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::EC2::SecurityGroup.Name"

    def __init__(self):
        super().__init__(
            format="AWS::EC2::SecurityGroup.Name",
            pattern=r"^[a-zA-Z0-9 \._\-:\/()#\,@\[\]+=&;\{\}!\$\*]+$",
        )
