"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_apigateway_authorizer
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class AuthorizerTtl(CfnLintJsonSchema):
    id = "E3718"
    shortdesc = "Validate API Gateway Authorizer TTL based on type"
    description = (
        "AuthorizerResultTtlInSeconds maximum of 3600 only applies "
        "to TOKEN and REQUEST authorizers."
    )
    source_url = (
        "https://docs.aws.amazon.com/apigateway/latest/api/API_CreateAuthorizer.html"
    )
    tags = ["resources", "apigateway"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ApiGateway::Authorizer/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_apigateway_authorizer,
                filename="ttl.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        ttl = instance.get("AuthorizerResultTtlInSeconds")
        auth_type = instance.get("Type")
        return (
            f"AuthorizerResultTtlInSeconds {ttl} "
            f"exceeds maximum of 3600 for {auth_type!r} authorizers"
        )
