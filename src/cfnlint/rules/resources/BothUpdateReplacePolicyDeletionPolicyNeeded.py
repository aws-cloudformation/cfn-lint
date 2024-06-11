"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.resources as resources_schemas
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class UpdateReplacePolicyDeletionPolicy(CfnLintJsonSchema):
    """Check resources with UpdateReplacePolicy/DeletionPolicy have both"""

    id = "W3011"
    shortdesc = "Check resources with UpdateReplacePolicy/DeletionPolicy have both"
    description = (
        "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources"
        " from deletion"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
    tags = ["resources", "updatereplacepolicy", "deletionpolicy"]

    def __init__(
        self,
    ) -> None:
        super().__init__(
            ["Resources/*"],
            SchemaDetails(resources_schemas, "update_policy_delete.json"),
            False,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "Both 'UpdateReplacePolicy' and 'DeletionPolicy' "
            "are needed to protect resource from deletion"
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        resource_type = instance.get("Type")
        if resource_type in [
            "AWS::Lambda::Version",
            "AWS::Lambda::LayerVersion",
        ]:
            return

        yield from super().validate(validator, keywords, instance, schema)
