"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from typing import Any

import cfnlint.data.schemas.other.resources
import cfnlint.data.schemas.other.step_functions
import cfnlint.helpers
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails
from cfnlint.schema.resolver import RefResolver


class Configuration(CfnLintJsonSchema):
    id = "E3601"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__(
            keywords=[
                "Resources/AWS::StepFunctions::StateMachine/Properties/Definition",
                "Resources/AWS::StepFunctions::StateMachine/Properties/DefinitionString",
            ],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.step_functions, "statemachine.json"
            ),
            all_matches=True,
        )

        store = {
            "definition": self.schema,
        }

        self.resolver = RefResolver.from_schema(self.schema, store=store)

    def _fix_message(self, err: ValidationError) -> ValidationError:
        if len(err.path) > 1:
            err.message = f"{err.message} at {'/'.join(err.path)!r}"
        for i, c_err in enumerate(err.context):
            err.context[i] = self._fix_message(c_err)
        return err

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        # First time child rules are configured against the rule
        # so we can run this now
        add_path_to_message = False
        if validator.is_type(instance, "string"):
            try:
                step_validator = validator.evolve(
                    context=validator.context.evolve(
                        functions=[],
                    ),
                    resolver=self.resolver,
                    schema=self.schema,
                )
                instance = json.loads(instance)
                add_path_to_message = True
            except json.JSONDecodeError:
                return
        else:
            step_validator = validator.evolve(
                resolver=self.resolver,
                schema=self.schema,
            )

        for err in step_validator.iter_errors(instance):
            if add_path_to_message:
                err = self._fix_message(err)
            if not err.validator.startswith("fn_") and err.validator not in ["cfnLint"]:
                err.rule = self

            yield self._clean_error(err)
