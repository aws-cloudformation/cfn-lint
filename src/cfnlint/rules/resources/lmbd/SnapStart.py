"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class SnapStart(CfnLintKeyword):
    """Check if Lambda SnapStart is properly configured"""

    id = "W2530"
    shortdesc = "Validate that SnapStart is properly configured"
    description = (
        "To properly leverage SnapStart, you must configure both the lambda function "
        "and attach a Lambda version resource"
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html"
    tags = ["resources", "lambda"]

    def __init__(self):
        super().__init__(
            [
                "Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn",
                "Resources/AWS::Serverless::Function/Properties/SnapStart/ApplyOn",
            ]
        )

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        if instance != "PublishedVersions":
            return

        resource_name: str = str(validator.context.path.path[1])
        resource_type: str = str(validator.context.path.cfn_path[1])

        # For AWS::Serverless::Function, check for AutoPublishAlias
        # which is the SAM mechanism that publishes a version
        if resource_type == "AWS::Serverless::Function":
            resources = validator.cfn.template.get("Resources", {})
            if not isinstance(resources, dict):
                return

            # If Resources is an intrinsic function, we can't evaluate it
            fn_key, _ = is_function(resources)
            if fn_key is not None:
                return

            resource = resources.get(resource_name, {})
            if not isinstance(resource, dict):
                return

            # If resource is an intrinsic function, we can't evaluate it
            fn_key, _ = is_function(resource)
            if fn_key is not None:
                return

            properties = resource.get("Properties", {})
            if not isinstance(properties, dict):
                return

            # If properties is an intrinsic function, we can't evaluate it
            fn_key, _ = is_function(properties)
            if fn_key is not None:
                return

            # AutoPublishAlias causes SAM to generate AWS::Lambda::Version
            # and AWS::Lambda::Alias resources
            if properties.get("AutoPublishAlias") is not None:
                return

            yield ValidationError(
                "'SnapStart' is enabled but 'AutoPublishAlias' is not configured",
            )
            return

        # For AWS::Lambda::Function, check for attached AWS::Lambda::Version
        lambda_version_type = "AWS::Lambda::Version"
        if list(
            validator.cfn.get_resource_children(resource_name, [lambda_version_type])
        ):
            return

        yield ValidationError(
            f"'SnapStart' is enabled but an {lambda_version_type!r} "
            "resource is not attached",
        )
