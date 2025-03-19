"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class ResourcePolicyResourceArn(CfnLintKeyword):

    id = "E3514"
    shortdesc = "Validate IAM resource policy resource ARNs"
    description = "Validates an IAM resource policy has a compliant resource ARN"
    source_url = (
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html"
    )
    tags = ["parameters", "iam"]

    def __init__(self) -> None:
        super().__init__(
            [
                "AWS::IAM::Policy/Properties/PolicyDocument/Statement/Resource",
            ]
        )

    # pylint: disable=unused-argument
    def validate(
        self, validator: Validator, aZ: Any, arn: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(arn, "string"):
            return

        if not len(validator.context.path.cfn_path) >= 2:
            return

        patrn: str = (
            "^(arn:aws[A-Za-z\\-]*?:[^:]+:[^:]*(:(?:\\d{12}|\\*|aws)?:.+|)|\\*)$"
        )
        if validator.context.path.cfn_path[1] == "AWS::S3::BucketPolicy":
            patrn = "^arn:aws[A-Za-z\\-]*?:[^:]+:[^:]*(:(?:\\d{12}|\\*|aws)?:.+|)$"

        if not re.match(patrn, arn):
            yield ValidationError(
                f"{arn!r} does not match {patrn!r}",
                rule=self,
            )
