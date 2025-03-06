"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_codebuild_project
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ProjectS3Location(CfnLintJsonSchema):
    id = "E3636"
    shortdesc = "Validate CodeBuild projects using S3 also have Location"
    description = "When using 'S3' for 'Type' then you must also specify " "'Location'"
    tags = ["resources", "codebuild"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::CodeBuild::Project/Properties/Artifacts",
                "Resources/AWS::CodeBuild::Project/Properties/Source",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_codebuild_project,
                filename="s3_locations.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return f"{err.message} when using 'Type' of 'S3'"
