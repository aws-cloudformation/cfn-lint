"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_autoscaling_scalingpolicy
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ScalingPolicyTargetTrackingAsg(CfnLintJsonSchema):
    id = "E3712"
    shortdesc = "TargetTrackingScaling policy requires ASG MaxSize greater than MinSize"
    description = (
        "When using a TargetTrackingScaling policy the referenced "
        "AutoScalingGroup must have MaxSize different from MinSize "
        "to allow scaling"
    )
    source_url = "https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html"
    tags = ["resources", "autoscaling"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::AutoScaling::ScalingPolicy/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_autoscaling_scalingpolicy,
                filename="policy_target_tracking_asg.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "TargetTrackingScaling policy requires the referenced "
            "AutoScalingGroup to have MaxSize greater than MinSize"
        )

    def _clean_error(self, err: ValidationError):
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
