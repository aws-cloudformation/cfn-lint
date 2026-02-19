"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FunctionLogLevelLogFormat(CfnLintJsonSchema):
    id = "E3696"
    shortdesc = "LogLevel is not supported when LogFormat is set to Text"
    description = (
        "LogLevel is not supported when LogFormat is set to 'Text'. "
        "Remove LogLevel from your request or change the LogFormat to 'JSON'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Function/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="loglevel_logformat.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "LogLevel is not supported when LogFormat is set to 'Text'. "
            "Remove LogLevel from your request or change the LogFormat to 'JSON'"
        )
