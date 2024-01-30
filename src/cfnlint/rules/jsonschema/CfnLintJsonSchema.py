"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, Sequence, Dict

from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._validators import type
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.rules.jsonschema.CfnLint import _pattern
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword
from collections import namedtuple

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
        self.all_matches = all_matches
        self._schema: Any = {}

        if schema_details:
            self._schema = load_resource(
                schema_details.module,
                filename=schema_details.filename,
            )

        for keyword in self.keywords:
            fn_name = _pattern.sub("", keyword)
            setattr(self, fn_name, self.iter_errors)

        self.validators["type"] = type

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
                err.rule = self
                errs = [err]

        yield from iter(errs)

    def iter_errors(self, validator, keywords, instance, schema):
        # if the schema has a description will only replace the message with that
        # description and use the best error for the location information

        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self.schema,
            context=validator.context.evolve(functions=[]),
        )

        yield from self._iter_errors(cfn_validator, instance)
