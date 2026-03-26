"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_apigateway_method
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class MethodAuthorizerType(CfnLintJsonSchema):
    id = "E3708"
    shortdesc = "API Gateway Method AuthorizationType must match Authorizer Type"
    description = (
        "When using AuthorizationType 'CUSTOM', the referenced Authorizer "
        "must have Type 'TOKEN' or 'REQUEST'. When using AuthorizationType "
        "'COGNITO_USER_POOLS', the Authorizer must have Type 'COGNITO_USER_POOLS'."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html"
    tags = ["resources", "apigateway"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ApiGateway::Method/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_apigateway_method,
                filename="method_authorizer_type.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
