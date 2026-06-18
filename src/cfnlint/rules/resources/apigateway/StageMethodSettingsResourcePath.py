"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_apigateway_stage
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class StageMethodSettingsResourcePath(CfnLintJsonSchema):
    id = "E3723"
    shortdesc = "ResourcePath must start with / when method settings are configured"
    description = (
        "When an API Gateway MethodSettings entry includes actual setting "
        "properties (LoggingLevel, MetricsEnabled, etc.), the ResourcePath "
        "must match the pattern '^/.*$'."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-methodsetting.html"
    tags = ["properties", "apigateway"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ApiGateway::Stage/Properties/MethodSettings/*",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_apigateway_stage,
                filename="method_settings_resource_path.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
