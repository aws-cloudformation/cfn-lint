"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FunctionZipfileRuntimeEnum(CfnLintJsonSchema):
    id = "E3677"
    shortdesc = "Validate Lambda using ZipFile requires an allowable runtime"
    description = (
        "Using the ZipFile attribute requires a javascript or "
        "python runtime to be specified"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Function/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="zipfile_runtime_enum.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
