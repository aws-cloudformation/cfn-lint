"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules import CloudFormationLintRule


class PropertyNames(CloudFormationLintRule):
    """Check maxLength values are correct"""

    def __init__(self, approaching_limit_rule: str | None = None) -> None:
        super().__init__()
        self.config["threshold"] = 0.9
        self.approaching_limit_rule = approaching_limit_rule

        self.child_rules = {}
        if self.approaching_limit_rule:
            self.child_rules[self.approaching_limit_rule] = None

    def _max_length(
        self, validator: Validator, mL: int, instance: Any, schema: dict[str, Any]
    ):
        if not validator.is_type(instance, "string"):
            return

        percent = len(instance) / mL
        if percent > 1:
            yield ValidationError(message=f"{instance!r} is longer than {mL}")
            return

        if percent > self.config["threshold"] and self.approaching_limit_rule:
            rule = self.child_rules.get(self.approaching_limit_rule)
            if not rule:
                return

            if hasattr(rule, "maxLength") and callable(getattr(rule, "maxLength")):
                validate = getattr(rule, "maxLength")
                yield from validate(validator, mL, instance, schema)
                return

            yield ValidationError(
                f"{instance!r} is approaching the max length of {mL}",
                rule=rule,
            )

    def propertyNames(
        self,
        validator: Validator,
        propertyNames: Any,
        instance: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        v = validator.extend(
            validators={
                "maxLength": self._max_length,
            }
        )({})

        for property in instance:
            yield from v.descend(
                instance=property,
                schema=propertyNames,
                path=property,
            )
