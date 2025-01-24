"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, Sequence

import cfnlint.data.schemas.extensions.aws_ecs_taskdefinition
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class LogConfiguration(CfnLintJsonSchema):
    id = "E3046"
    shortdesc = "Validate ECS task logging configuration for awslogs"
    description = (
        "When 'awslogs' the options 'awslogs-group' and 'awslogs-region' are required"
    )
    tags = ["resources"]

    def __init__(
        self, keywords: Sequence[str] | None = None, all_matches: bool = False
    ) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions/*/LogConfiguration"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_taskdefinition,
                filename="logging_configuration.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        # if the schema has a description will only replace the message with that
        # description and use the best error for the location information
        if not self._use_schema_arg:
            schema = self._schema

        cfn_validator = self.extend_validator(
            validator=validator.evolve(
                function_filter=validator.function_filter.evolve(
                    validate_dynamic_references=False,
                    add_cfn_lint_keyword=False,
                )
            ),
            schema=schema,
            context=validator.context.evolve(),
        )

        yield from self._iter_errors(cfn_validator, instance)
