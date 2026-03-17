"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_permission
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class PermissionPrincipal(CfnLintJsonSchema):
    id = "W3664"
    shortdesc = "Validate Lambda permission Principal matches SourceArn resource type"
    description = (
        "When configuring a Lambda permission with a SourceArn "
        "that references a resource, the Principal should match "
        "the service that owns that resource type"
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html"
    tags = ["resources", "lambda", "permission"]

    _type_to_principal: dict[str, str] = {
        "AWS::S3::Bucket": "s3.amazonaws.com",
        "AWS::SNS::Topic": "sns.amazonaws.com",
        "AWS::Events::Rule": "events.amazonaws.com",
        "AWS::ApiGateway::RestApi": "apigateway.amazonaws.com",
        "AWS::ApiGatewayV2::Api": "apigateway.amazonaws.com",
        "AWS::ElasticLoadBalancingV2::TargetGroup": (
            "elasticloadbalancing.amazonaws.com"
        ),
    }

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Permission/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_permission,
                filename="permission_principal.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
