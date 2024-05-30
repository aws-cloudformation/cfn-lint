"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules import CloudFormationLintRule


class FormatKeyword(CloudFormationLintRule):

    def __init__(self, format: str | None = None) -> None:
        super().__init__()
        self.format_keyword = format
        self.parent_rules = ["E1103"]
