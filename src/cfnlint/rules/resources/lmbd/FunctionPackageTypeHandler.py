"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FunctionPackageTypeHandler(CfnLintJsonSchema):
    id = "E4011"
    shortdesc = "Handler parameter is not supported for container images"
    description = "The Handler parameter is not supported for functions created with container images"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Function/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="packagetype_handler.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "The Handler parameter is not supported for functions created with container images"
