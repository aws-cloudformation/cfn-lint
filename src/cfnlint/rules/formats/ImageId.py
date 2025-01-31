"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import Validator
from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class ImageId(FormatKeyword):
    id = "E1152"
    shortdesc = "Validate AMI id format"
    description = "Check that a AMI id matches a pattern"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::EC2::Image.Id"

    def __init__(self):
        super().__init__(
            format="AWS::EC2::Image.Id", pattern=r"^ami-([0-9a-z]{8}|[0-9a-z]{17})$"
        )

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if validator.context.path.cfn_path_string == (
            "Resources/AWS::EC2::LaunchTemplate/"
            "Properties/LaunchTemplateData/ImageId"
        ):
            if instance.startswith("resolve:ssm"):
                return True

        if re.match(self.pattern, instance):
            return True

        return False
