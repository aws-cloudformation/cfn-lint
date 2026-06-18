"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

_setting_properties = {
    "CacheDataEncrypted",
    "CacheTtlInSeconds",
    "CachingEnabled",
    "DataTraceEnabled",
    "LoggingLevel",
    "MetricsEnabled",
    "ThrottlingBurstLimit",
    "ThrottlingRateLimit",
}


class StageMethodSettingsIgnored(CfnLintKeyword):
    id = "W3705"
    shortdesc = "MethodSettings entry is ignored without any setting properties"
    description = (
        "When an API Gateway MethodSettings entry specifies only HttpMethod "
        "and ResourcePath without any actual setting properties (LoggingLevel, "
        "MetricsEnabled, etc.), the entry is silently dropped by API Gateway."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-methodsetting.html"
    tags = ["properties", "apigateway"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ApiGateway::Stage/Properties/MethodSettings/*",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        has_settings = any(prop in instance for prop in _setting_properties)
        if has_settings:
            return

        if not instance:
            return

        yield ValidationError(
            "MethodSettings entry has no effect without a setting "
            "property (LoggingLevel, MetricsEnabled, CachingEnabled, etc.)",
        )
