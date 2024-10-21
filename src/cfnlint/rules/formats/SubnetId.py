"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import Validator
from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class SubnetId(FormatKeyword):
    id = "E1154"
    shortdesc = "Validate VPC subnet id format"
    description = "Check that a VPC subnet id matches a pattern"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::EC2::Subnet.Id"

    def __init__(self):
        super().__init__(format="AWS::EC2::Subnet.Id")

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if re.match(r"^subnet-(([0-9A-Fa-f]{8})|([0-9A-Fa-f]{17}))$", instance):
            return True

        return False
