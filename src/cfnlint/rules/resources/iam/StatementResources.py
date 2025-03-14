"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.iam
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails
from cfnlint.schema.resolver import RefResolver


class StatementResources(CfnLintJsonSchema):

    id = "I3510"
    shortdesc = "Validate statement resources match the actions"
    description = (
        "IAM policy statements have different constraints between actions and "
        "resources. This rule validates that actions that require an "
        "asterisk resource have an asterisk resource."
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html"
    tags = ["resources", "iam"]

    def __init__(self):
        super().__init__(
            ["AWS::IAM::Policy/Properties/PolicyDocument/Statement"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.iam, "policy_statement_resources.json"
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        if not validator.is_type(instance, "object"):
            return

        resolver = RefResolver.from_schema(self.schema)
        iam_validator = validator.evolve(
            resolver=resolver,
            schema=self.schema,
        )

        for err in iam_validator.iter_errors(instance):
            err.rule = self
            if err.validator == "contains":
                err.message = "'*' not found in array"
            yield self._clean_error(err)
