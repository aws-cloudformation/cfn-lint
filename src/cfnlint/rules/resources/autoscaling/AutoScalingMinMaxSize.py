"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_autoscaling_autoscalinggroup
from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails

# DesiredCapacity is compared with MinSize by "minimum" and MaxSize by "maximum"
_DESIRED_CAPACITY_BOUNDS = {"minimum": "MinSize", "maximum": "MaxSize"}


class AutoScalingMinMaxSize(CfnLintJsonSchema):
    id = "E3706"
    shortdesc = (
        "MaxSize must be greater than or equal to MinSize and "
        "DesiredCapacity must be between them"
    )
    description = (
        "Validates that AutoScaling group MaxSize is greater than or equal to "
        "MinSize and that DesiredCapacity is between MinSize and MaxSize"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-autoscaling-autoscalinggroup.html#cfn-autoscaling-autoscalinggroup-desiredcapacity"
    tags = ["resources", "autoscaling"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::AutoScaling::AutoScalingGroup/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_autoscaling_autoscalinggroup,
                filename="min_max_size.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message

    def _pairs_two_fn_ifs(self, instance: Any, err: ValidationError) -> bool:
        # cfnGather takes the first Fn::If branch of each gathered property on
        # its own, so two Fn::If values can be paired under conditions that
        # cannot both be true. Skip DesiredCapacity findings in that case.
        if list(err.path) != ["DesiredCapacity"] or not isinstance(instance, dict):
            return False
        bound = _DESIRED_CAPACITY_BOUNDS.get(str(err.validator))
        if bound is None:
            return False
        return (
            is_function(instance.get("DesiredCapacity"))[0] == "Fn::If"
            and is_function(instance.get(bound))[0] == "Fn::If"
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for err in super().validate(validator, keywords, instance, schema):
            if self._pairs_two_fn_ifs(instance, err):
                continue
            yield err
