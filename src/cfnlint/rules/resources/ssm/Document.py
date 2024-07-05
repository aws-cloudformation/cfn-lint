"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.ssm
from cfnlint.decode import decode_str
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails
from cfnlint.schema.resolver import RefResolver


class Document(CfnLintJsonSchema):
    id = "E3051"
    shortdesc = "Validate the structure of a SSM document"
    description = (
        "SSM documents are nested JSON/YAML in CloudFormation "
        "this rule adds validation to those documents"
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html"
    tags = ["properties", "ssm", "document"]

    def __init__(self):
        super().__init__(
            ["Resources/AWS::SSM::Document/Properties/Content"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.other.ssm,
                filename="document.json",
            ),
        )

        store = {
            "document": self.schema,
        }

        self.resolver = RefResolver.from_schema(self.schema, store=store)

    # pylint: disable=unused-argument
    def validate(
        self,
        validator: Validator,
        _: Any,
        instance: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        # First time child rules are configured against the rule
        # so we can run this now

        if validator.is_type(instance, "string"):
            ssm_validator = validator.evolve(
                context=validator.context.evolve(
                    functions=[],
                    strict_types=True,
                ),
                resolver=self.resolver,
                schema=self.schema,
            )

            instance, errs = decode_str(instance)
            if errs:
                yield ValidationError(
                    "Document is not of type 'object'",
                    validator="type",
                    rule=self,
                )
                return
        else:
            ssm_validator = validator.evolve(
                cfn=validator.cfn,
                context=validator.context.evolve(
                    strict_types=True,
                ),
                resolver=self.resolver,
                schema=self.schema,
            )

        for err in ssm_validator.iter_errors(instance):
            if not err.validator.startswith("fn_") and err.validator not in ["cfnLint"]:
                err.rule = self
            yield err
