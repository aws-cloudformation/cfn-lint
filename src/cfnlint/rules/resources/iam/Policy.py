"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from typing import Any

from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema
from cfnlint.schema.resolver import RefResolver


# pylint: disable=unused-argument
def _scalar_or_array(validator: Validator, subschema: Any, instance: Any, schema: Any):
    if validator.is_type(instance, "array"):
        for index, i in enumerate(instance):
            yield from validator.descend(i, subschema, path=index)
    else:
        yield from validator.descend(instance, subschema)


class Policy(CfnLintJsonSchema):
    """Check IAM policies"""

    def __init__(
        self,
        keywords: list[str] | None = None,
        schema_name: str | None = None,
        schema_file: str | None = None,
    ):
        super().__init__(keywords)

        if schema_name and schema_file:
            policy_schema = load_resource(
                "cfnlint.data.schemas.other.iam", "policy.json"
            )
            self.identity_schema = load_resource(
                "cfnlint.data.schemas.other.iam", schema_file
            )
            store = {
                "policy": policy_schema,
                schema_name: self.identity_schema,
            }
            # To reduce reduntant schemas use a schema resolver
            # this is deprecated in 4.18 of jsonschema
            self.resolver = RefResolver.from_schema(self.identity_schema, store=store)

    # pylint: disable=unused-argument
    def validate(
        self,
        validator: Validator,
        policy_type: Any,
        policy: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        # First time child rules are configured against the rule
        # so we can run this now
        if validator.is_type(policy, "string"):
            try:
                iam_validator = validator.extend(
                    validators={
                        "scalarOrArray": _scalar_or_array,
                    },
                )(schema=self.identity_schema).evolve(
                    context=validator.context.evolve(
                        functions=[],
                    ),
                    resolver=self.resolver,
                )
                policy = json.loads(policy)
            except json.JSONDecodeError:
                return
        else:
            iam_validator = validator.extend(
                validators={
                    "scalarOrArray": _scalar_or_array,
                },
            )(schema=self.identity_schema).evolve(
                cfn=validator.cfn,
                context=validator.context,
                resolver=self.resolver,
            )

        for err in iam_validator.iter_errors(policy):
            if not err.validator.startswith("fn_") and err.validator not in ["cfnLint"]:
                err.rule = self
            yield err
