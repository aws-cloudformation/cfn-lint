"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class DistributionCacheBehaviorForwardedValuesIgnored(CfnLintKeyword):
    id = "W3704"
    shortdesc = "ForwardedValues is ignored when CachePolicyId is specified"
    description = (
        "When a CloudFront cache behavior specifies a CachePolicyId, "
        "ForwardedValues is silently ignored. Remove ForwardedValues "
        "or remove CachePolicyId."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-cachebehavior.html"
    tags = ["properties", "cloudfront"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig/DefaultCacheBehavior",
                "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig/CacheBehaviors/*",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        if "CachePolicyId" not in instance:
            return

        if "ForwardedValues" not in instance:
            return

        yield ValidationError(
            "'ForwardedValues' is ignored when 'CachePolicyId' is specified",
            path=["ForwardedValues"],
        )
