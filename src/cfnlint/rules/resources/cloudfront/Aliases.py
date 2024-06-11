"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.helpers import REGEX_DYN_REF
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class Aliases(CfnLintKeyword):
    """Check if CloudFront Aliases are valid domain names"""

    id = "E3013"
    shortdesc = "CloudFront Aliases"
    description = "CloudFront aliases should contain valid domain names"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-distributionconfig.html#cfn-cloudfront-distribution-distributionconfig-aliases"
    tags = ["properties", "cloudfront"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=[
                "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig/Aliases/*"
            ]
        )

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        if isinstance(instance, str):
            if re.match(REGEX_DYN_REF, instance):
                return
            for err in validator.descend(
                instance=instance,
                schema={
                    "pattern": "^(?!.*(?:\\.\\*\\.)).*",
                },
            ):
                err.rule = self
                yield err

            for err in validator.descend(
                instance=instance,
                schema={
                    # ruff: noqa: E501
                    "pattern": "^(?:[a-z0-9\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$",
                },
            ):
                err.rule = self
                yield err
