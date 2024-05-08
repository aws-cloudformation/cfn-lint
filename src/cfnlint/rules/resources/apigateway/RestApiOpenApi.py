"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_apigateway_restapi
from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class RestApiOpenApi(CfnLintJsonSchema):
    id = "E3660"
    shortdesc = "RestApi requires a name when not using an OpenAPI specification"
    description = (
        "When using AWS::ApiGateway::RestApi you have to provide 'Name' "
        "if you don't provide 'Body' or 'BodyS3Location'"
    )
    tags = ["resources", "apigateway"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ApiGateway::RestApi/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_apigateway_restapi,
                filename="openapi_properties.json",
            ),
            all_matches=False,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return f"{err.message} when not specifying one of ['Body', 'BodyS3Location']"
