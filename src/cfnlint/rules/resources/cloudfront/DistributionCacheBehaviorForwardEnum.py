"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_cloudfront_distribution
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DistributionCacheBehaviorForwardEnum(CfnLintJsonSchema):
    id = "E3722"
    shortdesc = "Cookies Forward must be a valid enum when CachePolicyId is absent"
    description = (
        "When a CloudFront cache behavior does not specify a CachePolicyId, "
        "the ForwardedValues Cookies Forward property must be one of "
        "'all', 'none', or 'whitelist'."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-cookies.html"
    tags = ["properties", "cloudfront"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig/DefaultCacheBehavior",
                "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig/CacheBehaviors/*",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_cloudfront_distribution,
                filename="forward_enum.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
