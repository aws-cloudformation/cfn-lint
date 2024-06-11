"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class RoleArnPattern(CfnLintKeyword):
    """Check role arn pattern"""

    id = "E3511"
    shortdesc = "Validate IAM role arn pattern"
    description = "Validate an IAM role arn pattern matches"
    source_url = (
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html"
    )
    tags = ["parameters", "iam"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::Backup::BackupSelection/Properties/BackupSelection/IamRoleArn",
                "Resources/AWS::Batch::ComputeEnvironment/Properties/ComputeResources/SpotIamFleetRole",
                "Resources/AWS::Batch::ComputeEnvironment/Properties/ServiceRole",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/IamFleetRole",
                "Resources/AWS::ECS::TaskDefinition/Properties/ExecutionRoleArn",
                "Resources/AWS::S3::Bucket/Properties/ReplicationConfiguration/Role",
            ]
        )

    # pylint: disable=unused-argument
    def validate(
        self, validator: Validator, aZ: Any, arn: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(arn, "string"):
            return

        patrn = "^arn:(aws[a-zA-Z-]*)?:iam::\\d{12}:role/[a-zA-Z_0-9+=,.@\\-_/]+$"

        if not re.match(patrn, arn):
            yield ValidationError(
                f"{arn!r} does not match {patrn!r}",
                rule=self,
            )
