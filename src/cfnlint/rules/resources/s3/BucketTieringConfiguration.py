"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class BucketTieringConfiguration(CfnLintKeyword):
    id = "E3061"
    shortdesc = "Validate the days for tierings in IntelligentTieringConfigurations"
    description = (
        "When using AWS::S3::Bucket to configure IntelligentTieringConfigurations "
        "the Tierings have minimum and maximum values"
    )
    source_url = "https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html"
    tags = ["resources", "s3"]

    def __init__(self):
        super().__init__(
            [
                "Resources/AWS::S3::Bucket/Properties/IntelligentTieringConfigurations/*/Tierings/*"
            ]
        )

        self._tierings = {
            "ARCHIVE_ACCESS": {
                "minimum": 90,
                "maximum": 730,
            },
            "DEEP_ARCHIVE_ACCESS": {
                "minimum": 180,
                "maximum": 730,
            },
        }

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for archive_access, archive_access_validator in get_value_from_path(
            validator, instance, deque(["AccessTier"])
        ):
            if not validator.is_type(archive_access, "string"):
                continue
            for days, days_validator in get_value_from_path(
                archive_access_validator, instance, deque(["Days"])
            ):
                if validator.is_type(days, "string"):
                    try:
                        days = int(days)
                    except Exception:
                        return

                if not validator.is_type(days, "integer"):
                    continue

                days_validator = validator.evolve(
                    schema=self._tierings.get(archive_access, {})
                )

                for err in days_validator.iter_errors(days):
                    err.path = deque(["Days"])
                    err.rule = self
                    yield err
