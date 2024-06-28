"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import namedtuple
from typing import Any, Sequence

from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.Base import BaseJsonSchema

SchemaDetails = namedtuple("SchemaDetails", ["module", "filename"])


class CfnLintJsonSchema(BaseJsonSchema):
    def __init__(
        self,
        keywords: Sequence[str] | None = None,
        schema_details: SchemaDetails | None = None,
        all_matches: bool = False,
    ) -> None:
        super().__init__()
        self.keywords = keywords or []
        self.parent_rules = ["E1101"]
        self.all_matches = all_matches
        self._use_schema_arg = True
        self._schema: Any = {}

        if schema_details:
            self._schema = load_resource(
                schema_details.module,
                filename=schema_details.filename,
            )
            self._use_schema_arg = False

    @property
    def schema(self):
        return self._schema

    def message(self, instance: Any, err: ValidationError) -> str:
        return self.shortdesc

    def _iter_errors(self, validator, instance):
        errs = list(validator.iter_errors(instance))
        if not self.all_matches:
            err = best_match(errs)
            if err is not None:
                err.message = self.message(instance, err)
                err.context = []
                err.rule = self
                yield err
                return

        for err in errs:
            yield self._clean_error(err)

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
            context=validator.context.evolve(
                functions=[],
                strict_types=True,
            ),
        )

        yield from self._iter_errors(cfn_validator, instance)
