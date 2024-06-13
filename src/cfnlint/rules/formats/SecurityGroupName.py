"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import Validator
from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class SecurityGroupName(FormatKeyword):
    id = "E1153"
    shortdesc = "Validate security group name"
    description = "Security group names have to valid pattern"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::EC2::SecurityGroup.GroupName"

    def __init__(self):
        super().__init__(format="AWS::EC2::SecurityGroup.GroupName")

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if re.match(r"^[a-zA-Z0-9 \._\-:\/()#\,@\[\]+=&;\{\}!\$\*]+$", instance):
            return True

        return False
