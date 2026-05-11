"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class AutoScalingGroupHealthCheckType(CfnLintKeyword):
    id = "E3056"
    shortdesc = "EC2 health check type cannot be combined with other types"
    description = (
        "When specifying multiple health check types for an "
        "Auto Scaling group, EC2 cannot be combined with "
        "other health check types."
    )
    source_url = "https://docs.aws.amazon.com/autoscaling/ec2/userguide/health-checks-overview.html"
    tags = ["resources", "autoscaling"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::AutoScaling::AutoScalingGroup/Properties/HealthCheckType",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, str):
            return

        if "," not in instance:
            return

        parts = [p.strip() for p in instance.split(",")]
        if "EC2" in parts and len(parts) > 1:
            yield ValidationError(
                "EC2 cannot be combined with other health check types. "
                f"Got {instance!r}"
            )
