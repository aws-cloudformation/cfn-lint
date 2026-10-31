"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_applicationautoscaling_scalingpolicy
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ScalingPolicyScalingTargetConsistency(CfnLintJsonSchema):
    id = "E3726"
    shortdesc = (
        "ScalingTargetId and the ResourceId trio must agree when both are specified"
    )
    description = (
        "When an AWS::ApplicationAutoScaling::ScalingPolicy specifies both "
        "ScalingTargetId and ResourceId, the ResourceId, ScalableDimension, "
        "and ServiceNamespace must match the values of the "
        "AWS::ApplicationAutoScaling::ScalableTarget referenced by "
        "ScalingTargetId, mirroring the service-side validation that fails "
        "with 'ResourceId does not match ScalingTargetId'."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html"
    tags = ["resources", "applicationautoscaling"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ApplicationAutoScaling::ScalingPolicy/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_applicationautoscaling_scalingpolicy,
                filename="scaling_policy_scaling_target_consistency.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        prop = err.path[-1] if err.path else "property"
        return (
            f"{prop} {err.instance!r} does not match ScalingTargetId. "
            "When both ScalingTargetId and ResourceId are specified, "
            "ResourceId, ScalableDimension, and ServiceNamespace must agree "
            "with the referenced AWS::ApplicationAutoScaling::ScalableTarget."
        )

    def _clean_error(self, err: ValidationError):
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
