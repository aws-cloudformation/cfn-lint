"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations
import pathlib
from typing import Any, Sequence

from cfnlint.helpers import load_plugins, load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._validators import type
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.jsonschema.CfnLint import _pattern


class CfnLintJsonSchema(BaseJsonSchema):
    def __init__(self, keywords: Sequence[str] | None = None, all_matches: bool = False) -> None:
        super().__init__()
        self.keywords = keywords
        self.all_matches = all_matches

        if keywords:
            if len(keywords) > 1:
                raise ValueError("Only provide 1 keyword")
            for keyword in keywords:
                schema_split = keyword.split("/")
                if len(schema_split) > 1:
                    self._schema = load_resource(
                        f"cfnlint.data.schemas.extensions.{schema_split[0]}",
                        filename=(f"{schema_split[1]}.json"),
                    )
                
                fn_name = _pattern.sub("", keyword)
                setattr(self, fn_name, self._iter_errors)

        self.validators["type"] = type

    @property
    def schema(self):
        return self._schema

    def message(self, instance: Any, err: ValidationError) -> str:
        return self.shortdesc

    def _iter_errors(self, validator, keywords, instance, schema):
        # if the schema has a description will only replace the message with that
        # description and use the best error for the location information
        if schema is None:
            schema = self.schema

        cfn_validator = self.extend_validator(
            validator=validator,
            schema=schema,
            context=validator.context.evolve(functions=[]),
        )

        errs = list(cfn_validator.iter_errors(instance))
        if not self.all_matches:
            err = best_match(errs)
            if err is not None:
                err.message = self.message(instance, err)
                err.rule = self
                errs = [err]

        yield from iter(errs)
