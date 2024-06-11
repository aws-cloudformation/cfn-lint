"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.resources
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class CfnInit(CfnLintJsonSchema):
    """Check CloudFormation Init items"""

    id = "E3009"
    shortdesc = "Check CloudFormation init configuration"
    description = "Validate that the items in a CloudFormation init adhere to standards"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html#aws-resource-cloudformation-init-syntax"
    tags = ["resources", "cloudformation init"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/*/Metadata/AWS::CloudFormation::Init"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.resources, "cfn_init.json"
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(functions=list(FUNCTIONS)),
        )

        yield from super()._iter_errors(cfn_validator, instance)
