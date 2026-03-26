"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class AutoScalingMinMaxSize(CfnLintKeyword):
    id = "E3706"
    shortdesc = "MaxSize must be greater than or equal to MinSize"
    description = (
        "Validates that AutoScaling group MaxSize is greater than or equal to MinSize"
    )
    source_url = "https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-simple-step.html"
    tags = ["resources", "autoscaling"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::AutoScaling::AutoScalingGroup/Properties",
            ],
        )

    def validate(
        self,
        validator: Validator,
        keywords: Any,
        instance: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        for min_value, min_validator in get_value_from_path(
            validator, instance, deque(["MinSize"])
        ):
            if not isinstance(min_value, (str, int, float)):
                continue
            for max_value, _ in get_value_from_path(
                min_validator, instance, deque(["MaxSize"])
            ):
                if not isinstance(max_value, (str, int, float)):
                    continue
                try:
                    min_int = int(min_value)
                    max_int = int(max_value)
                except (ValueError, TypeError):
                    continue

                if max_int < min_int:
                    yield ValidationError(
                        f"MaxSize ({max_int}) must be greater than "
                        f"or equal to MinSize ({min_int})",
                        path=deque(["MaxSize"]),
                        rule=self,
                    )
