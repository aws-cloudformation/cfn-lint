"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_apigateway_method
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class MethodAuthorizerRestApi(CfnLintJsonSchema):
    id = "E3699"
    shortdesc = "API Gateway Method and Authorizer must use the same RestApi"
    description = (
        "When an API Gateway Method references an Authorizer, both "
        "must reference the same RestApi. A mismatch causes a "
        "deployment failure."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html"
    tags = ["resources", "apigateway"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ApiGateway::Method/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_apigateway_method,
                filename="method_authorizer_rest_api.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
