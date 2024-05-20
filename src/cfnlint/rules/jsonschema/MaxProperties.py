"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class MaxProperties(CloudFormationLintRule):
    """Check maxProperties are correct"""

    def __init__(self, approaching_limit_rule: str | None = None) -> None:
        super().__init__()
        self.config["threshold"] = 0.9

        self.approaching_limit_rule = approaching_limit_rule

        self.child_rules = {}
        if approaching_limit_rule:
            self.child_rules[approaching_limit_rule] = None

    # pylint: disable=unused-argument
    def maxProperties(self, validator, mP, instance, schema):
        if not validator.is_type(instance, "object"):
            return

        percent = len(instance) / mP
        if percent > 1:
            yield ValidationError(
                (
                    f"{validator.context.path.path_string!r} "
                    f"has more than {mP!r} properties"
                )
            )
            return
        if percent > self.config["threshold"]:
            rule = self.child_rules.get(self.approaching_limit_rule)
            if not rule:
                return

            if hasattr(rule, "maxProperties") and callable(
                getattr(rule, "maxProperties")
            ):
                validate = getattr(rule, "maxProperties")
                yield from validate(validator, mP, instance, schema)
                return

            yield ValidationError(
                (
                    f"{validator.context.path.path_string!r} "
                    f"is approaching the limit of {mP!r} properties"
                ),
                rule=rule,
            )
