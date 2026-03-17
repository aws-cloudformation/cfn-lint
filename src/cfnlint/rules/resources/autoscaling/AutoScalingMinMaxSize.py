"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_autoscaling_autoscalinggroup
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class AutoScalingMinMaxSize(CfnLintJsonSchema):
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
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_autoscaling_autoscalinggroup,
                filename="min_max_size.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
