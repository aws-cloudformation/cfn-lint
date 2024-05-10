"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, Sequence

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class CfnLintKeyword(CloudFormationLintRule):
    def __init__(self, keywords: Sequence[str] | None = None) -> None:
        super().__init__()
        self.keywords = keywords or []
        self.parent_rules = ["E1101"]

    def message(self, instance: Any, err: ValidationError) -> str:
        return self.shortdesc
