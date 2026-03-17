"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_lambda_permission
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class PermissionSourceAccount(CfnLintJsonSchema):
    id = "W3663"
    shortdesc = "Validate SourceAccount is required property"
    description = (
        "When configuration a Lambda permission with a SourceArn "
        "that doesn't have an AccountId you should also specify "
        "the SourceAccount"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-sourceaccount"
    tags = ["resources", "lambda", "permission"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Permission/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_permission,
                filename="permission_source_account.json",
            ),
        )
