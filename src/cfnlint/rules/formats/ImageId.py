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
    source_url = "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html"

    def __init__(self):
        super().__init__(format="AWS::EC2::Image.Id")

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if re.match(r"^ami-(([0-9a-z]{8})|([0-9a-z]{17}))$", instance):
            return True

        return False
