"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import regex as re

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class RoleArnPattern(BaseJsonSchema):
    """Check role arn pattern"""

    id = "E3511"
    shortdesc = "Validate IAM role arn pattern"
    description = "Validate an IAM role arn pattern matches"
    source_url = (
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html"
    )
    tags = ["parameters", "iam"]

    # pylint: disable=unused-argument
    def iamrolearn(self, validator, aZ, arn, schema):
        if not validator.is_type(arn, "string"):
            return

        patrn = "^arn:(aws[a-zA-Z-]*)?:iam::\\d{12}:role/[a-zA-Z_0-9+=,.@\\-_/]+$"

        if not re.match(patrn, arn):
            yield ValidationError(f"{arn!r} does not match {patrn!r}")
