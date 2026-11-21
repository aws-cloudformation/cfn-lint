"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FunctionZipfileHandler(CfnLintJsonSchema):
    id = "E3726"
    shortdesc = "Inline Lambda code requires an index handler"
    description = (
        "CloudFormation writes inline Lambda code to an index file. "
        "The Handler must start with 'index.' when Code.ZipFile or InlineCode is used."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-lambda-function-code.html#cfn-lambda-function-code-zipfile"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Lambda::Function/Properties",
                "Resources/AWS::Serverless::Function/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="zipfile_handler.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "Inline Lambda code requires Handler to start with 'index.'"
