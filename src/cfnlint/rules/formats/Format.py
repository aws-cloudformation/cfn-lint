"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._keywords import format as parent_format
from cfnlint.rules import CloudFormationLintRule


class Format(CloudFormationLintRule):
    id = "E1103"
    shortdesc = "Validate the format of a value"
    description = "Parent rule for validating the format keyword in schemas"
    tags = []

    def format(
        self, validator: Validator, format: Any, instance: Any, schema: dict[str, Any]
    ):
        if validator.format_checker is not None:  # type: ignore
            if format in validator.format_checker.checkers:
                yield from parent_format(validator, format, instance, schema)
                return

        for rule in self.child_rules.values():
            if rule is None:
                continue
            if not rule.id:
                continue

            if format == rule.format_keyword:  # type: ignore
                if not rule.format(validator, instance):  # type: ignore
                    yield ValidationError(
                        f"{instance!r} is not a {format!r}",
                        rule=rule,
                    )
