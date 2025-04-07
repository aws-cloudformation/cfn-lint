"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_targetgroup
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class TargetGroupProtocolRestrictions(CfnLintJsonSchema):
    id = "E3683"
    shortdesc = "Validate target group protocol property restrictions"
    description = (
        "When a TargetGroup protocol is HTTP/HTTPS or GENEVE "
        "there are different restrictions on properties."
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ElasticLoadBalancingV2::TargetGroup/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_targetgroup,
                filename="protocol_restrictions.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for err in super().validate(validator, keywords, instance, schema):
            if not err.schema:
                err.message = (
                    f"Additional properties are not allowed ({err.path[0]!r} "
                    "was unexpected)"
                )
                err.validator = "additionalProperties"
            yield err
