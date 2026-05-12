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
        "AWS::ApiGateway::RestApi": "apigateway.amazonaws.com",
        "AWS::ApiGatewayV2::Api": "apigateway.amazonaws.com",
        "AWS::Cognito::UserPool": "cognito-idp.amazonaws.com",
        "AWS::Config::ConfigRule": "config.amazonaws.com",
        "AWS::ElasticLoadBalancingV2::TargetGroup": (
            "elasticloadbalancing.amazonaws.com"
        ),
        "AWS::Events::Rule": "events.amazonaws.com",
        "AWS::IoT::TopicRule": "iot.amazonaws.com",
        "AWS::Logs::LogGroup": "logs.amazonaws.com",
        "AWS::S3::Bucket": "s3.amazonaws.com",
        "AWS::SNS::Topic": "sns.amazonaws.com",
    }

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Permission/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_permission,
                filename="permission_principal.json",
            ),
        )

    # Map from pattern back to friendly service name for error messages
    _pattern_to_friendly: dict[str, str] = {
        "^apigateway\\.amazonaws\\.com$": "apigateway.amazonaws.com",
        "^cognito-idp\\.amazonaws\\.com$": "cognito-idp.amazonaws.com",
        "^config\\.amazonaws\\.com$": "config.amazonaws.com",
        "^elasticloadbalancing\\.amazonaws\\.com$": (
            "elasticloadbalancing.amazonaws.com"
        ),
        "^events\\.amazonaws\\.com$": "events.amazonaws.com",
        "^iot\\.amazonaws\\.com$": "iot.amazonaws.com",
        "^logs(\\.[a-z]{2}(-gov|-iso[a-z]?)?-[a-z]+-[0-9]+)?\\.amazonaws\\.com$": (
            "logs.amazonaws.com or logs.<region>.amazonaws.com"
        ),
        "^s3\\.amazonaws\\.com$": "s3.amazonaws.com",
        "^sns\\.amazonaws\\.com$": "sns.amazonaws.com",
    }

    def message(self, instance: Any, err: ValidationError) -> str:
        pattern = err.validator_value if err.validator == "pattern" else ""
        friendly = self._pattern_to_friendly.get(pattern, "")
        if friendly:
            return (
                f"Principal {err.instance!r} does not match expected "
                f"service principal {friendly!r}"
            )
        return err.message
