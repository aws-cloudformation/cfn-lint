"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import Validator
from cfnlint.rules import CloudFormationLintRule


class FormatKeyword(CloudFormationLintRule):

    def __init__(self, format: str | None = None, pattern: str | None = None) -> None:
        super().__init__()
        self.format_keyword = format
        self.parent_rules = ["E1103"]
        self.pattern = pattern or r""

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if re.match(self.pattern, instance):
            return True

        return False
