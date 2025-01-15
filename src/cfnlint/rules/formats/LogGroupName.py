"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import Validator
from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class LogGroupName(FormatKeyword):
    id = "E1155"
    shortdesc = "Validate CloudWatch logs group name"
    description = "Check that a CloudWatch log group name matches a pattern"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::Logs::LogGroup.Name"

    def __init__(self):
        super().__init__(format="AWS::EC2::Subnet.Id")

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if re.match(r"^[\.\-_\/#A-Za-z0-9]{1,512}\Z", instance):
            return True

        return False
