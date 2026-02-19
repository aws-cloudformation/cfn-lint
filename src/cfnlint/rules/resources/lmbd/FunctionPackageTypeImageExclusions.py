"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FunctionPackageTypeImageExclusions(CfnLintJsonSchema):
    id = "E3685"
    shortdesc = "Container image functions cannot use Handler, Runtime, or Layers"
    description = (
        "Functions with PackageType 'Image' cannot specify "
        "Handler, Runtime, or Layers properties"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Function/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="packagetype_image_exclusions.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "Container image functions cannot specify "
            "Handler, Runtime, or Layers properties"
        )
