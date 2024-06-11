"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class RuleScheduleExpression(CfnLintKeyword):
    """Validate AWS Events Schedule expression format"""

    id = "E3027"
    shortdesc = "Validate AWS Event ScheduleExpression format"
    description = "Validate the formation of the AWS::Event ScheduleExpression"
    source_url = "https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html"
    tags = ["resources", "events"]

    def initialize(self, cfn):
        """Initialize the rule"""
        self.__init__(["Resources/AWS::Events::Rule/Properties/ScheduleExpression"])

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        # Value is either "cron()" or "rate()"
        if not validator.is_type(instance, "string"):
            return

        if instance.startswith("rate(") and instance.endswith(")"):
            yield from self._check_rate(instance)
        elif instance.startswith("cron(") and instance.endswith(")"):
            yield from self._check_cron(instance)
        else:
            yield ValidationError(f"{instance!r} has to be either 'cron()' or 'rate()'")

    def _check_rate(self, value):
        """Check Rate configuration"""
        # Extract the expression from rate(XXX)
        rate_expression = value[value.find("(") + 1 : value.find(")")]

        if not rate_expression:
            yield ValidationError(
                message=f"{rate_expression!r} is not of type 'string'",
            )
            return

        # Rate format: rate(Value Unit)
        items = rate_expression.split(" ")

        if len(items) != 2:
            yield ValidationError(
                f"{rate_expression!r} has to be of format rate(Value Unit)"
            )
            return

        # Check the Value
        if not items[0].isdigit():
            extra_args = {
                "actual_type": type(items[0]).__name__,
                "expected_type": int.__name__,
            }
            yield ValidationError(
                message=f"{items[0]!r} is not of type 'integer'",
                extra_args=extra_args,
            )
            return

        if float(items[0]) <= 0:
            yield ValidationError(f"{items[0]!r} is less than the minimum of {0!r}")

        if float(items[0]) <= 1:
            valid_periods = ["minute", "hour", "day"]
        elif float(items[0]) > 1:
            valid_periods = ["minutes", "hours", "days"]
        # Check the Unit
        if items[1] not in valid_periods:
            yield ValidationError(f"{items[1]!r} is not one of {valid_periods!r}")

    def _check_cron(self, value):
        """Check Cron configuration"""
        # Extract the expression from cron(XXX)
        cron_expression = value[value.find("(") + 1 : value.find(")")]

        if not cron_expression:
            yield ValidationError(
                message=f"{cron_expression!r} is not of type 'string'",
            )
            return
        else:
            # Rate format: cron(Minutes Hours Day-of-month Month Day-of-week Year)
            items = cron_expression.split(" ")

            if len(items) != 6:
                yield ValidationError(
                    message=(
                        f"{items[0]!r} is not of length {6!r}. "
                        "(Minutes Hours Day-of-month Month Day-of-week Year)"
                    ),
                )
                return

            _, _, day_of_month, _, day_of_week, _ = cron_expression.split(" ")
            if day_of_month != "?" and day_of_week != "?":
                yield ValidationError(
                    message=(
                        f"{cron_expression[0]!r} specifies both "
                        "Day-of-month and Day-of-week. "
                        "(Minutes Hours Day-of-month Month Day-of-week Year)"
                    ),
                )
