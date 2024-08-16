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


class DistributionTargetOriginId(CfnLintKeyword):
    id = "E3057"
    shortdesc = "Validate that CloudFront TargetOriginId is a specified Origin"
    description = (
        "CloudFront TargetOriginId has to map to an Origin Id that "
        "is in the same DistributionConfig"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-defaultcachebehavior.html#cfn-cloudfront-distribution-defaultcachebehavior-targetoriginid"
    tags = ["properties", "cloudfront"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=[
                "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig"
            ]
        )

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for cache_origin_id, cache_validator in get_value_from_path(
            validator, instance, path=deque(["DefaultCacheBehavior", "TargetOriginId"])
        ):
            if not validator.is_type(cache_origin_id, "string"):
                continue
            origin_ids = []
            for origin_id, _ in get_value_from_path(
                cache_validator, instance, path=deque(["Origins", "*", "Id"])
            ):
                if not validator.is_type(origin_id, "string"):
                    break
                if origin_id == cache_origin_id:
                    break
                origin_ids.append(origin_id)
            else:
                for origin_id, _ in get_value_from_path(
                    cache_validator,
                    instance,
                    path=deque(["OriginGroups", "Items", "*", "Id"]),
                ):
                    if origin_id is None:
                        continue
                    if not validator.is_type(origin_id, "string"):
                        break
                    if origin_id == cache_origin_id:
                        break
                    origin_ids.append(origin_id)
                else:
                    yield ValidationError(
                        message=f"{cache_origin_id!r} is not one of {origin_ids!r}",
                        rule=self,
                        path_override=cache_validator.context.path.path,
                        validator="enum",
                    )
