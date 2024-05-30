"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import Validator
from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class SecuriyGroupId(FormatKeyword):
    id = "E1150"
    shortdesc = "Validate security group format"
    description = (
        "Security groups have to ref/gettatt to a security "
        "group or has the valid pattern"
    )
    tags = []

    def __init__(self):
        super().__init__(format="SecurityGroupId")

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if re.match(r"^sg-[a-z0-9]{8,17}$", instance):
            return True

        return False
