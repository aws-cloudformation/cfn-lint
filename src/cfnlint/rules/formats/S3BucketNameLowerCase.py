"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class S3BucketNameLowerCase(FormatKeyword):
    id = "W1161"
    shortdesc = "S3 bucket names should use lowercase letters"
    description = (
        "S3 bucket names with uppercase letters were allowed before March 2018 "
        "but are no longer recommended. New buckets must use lowercase only."
    )
    tags = ["resources", "s3"]
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::S3::Bucket.Name"

    def __init__(self):
        super().__init__(
            format="AWS::S3::Bucket.Name",
        )

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if instance != instance.lower():
            return False

        return True
