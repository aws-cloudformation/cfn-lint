"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

import regex as re

from cfnlint.helpers import REGEX_SUB_PARAMETERS, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class Sub(BaseFn):
    """Check if Sub values are correct"""

    id = "E1019"
    shortdesc = "Sub validation of parameters"
    description = "Making sure the sub function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub"]

    def __init__(self) -> None:
        super().__init__("Fn::Sub", ("string",), resolved_rule="W1031")
        self.sub_parameter_types = ["string", "integer", "number", "boolean"]
        self.child_rules.update(
            {
                "W1019": None,
                "W1020": None,
                "W1051": None,
            }
        )
        self._functions = [
            "Fn::Base64",
            "Fn::FindInMap",
            "Fn::GetAtt",
            "Fn::GetAZs",
            "Fn::If",
            "Fn::ImportValue",
            "Fn::Join",
            "Fn::Select",
            "Fn::Sub",
            "Fn::ToJsonString",
            "Fn::Transform",
            "Ref",
        ]

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        return {
            "type": ["array", "string"],
            "minItems": 2,
            "maxItems": 2,
            "fn_items": [
                {
                    "schema": {"type": "string"},
                },
                {
                    "functions": self._functions,
                    "schema": {
                        "type": ["object"],
                        "patternProperties": {
                            "[a-zA-Z0-9]+": {
                                "type": ["string"],
                            }
                        },
                        "additionalProperties": False,
                    },
                },
            ],
        }

    def _clean_error(
        self, err: ValidationError, instance: Any, param: Any
    ) -> ValidationError:
        err.message = err.message.replace(f"{instance!r}", f"{param!r}")
        err.instance = param
        err.path = deque([self.fn.name])
        err.schema_path = deque([])
        err.validator = self.fn.py
        return err

    def _validate_string(
        self, validator: Validator, key: str, instance: Any, sub_values: dict[str, Any]
    ) -> ValidationResult:
        params = re.findall(REGEX_SUB_PARAMETERS, instance)
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=self._functions,
                path=validator.context.path.descend(
                    path=key,
                ),
                strict_types=True,
            ),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
        )
        for param in params:
            param = param.strip()
            if "." in param:
                for err in validator.descend(
                    instance={"Fn::GetAtt": param},
                    schema={"type": ["string"]},
                ):
                    yield self._clean_error(err, {"Fn::GetAtt": param}, param)
            else:
                if param not in sub_values:
                    for err in validator.descend(
                        instance={"Ref": param},
                        schema={"type": ["string"]},
                    ):
                        yield self._clean_error(err, {"Ref": param}, param)

    def fn_sub(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        validator = validator.evolve(
            context=validator.context.evolve(strict_types=True),
        )
        errs = list(super().validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)
            return

        key, value = self.key_value(instance)
        sub_values = {}
        if validator.is_type(value, "array"):
            sub_values = value[1].copy()
            for sub_k, sub_v in value[1].items():
                fn_k, fn_v = is_function(sub_v)
                if fn_k == "Ref" and fn_v == sub_k:
                    del sub_values[sub_k]
            value = value[0]

        errs = list(self._validate_string(validator, key, value, sub_values))
        if errs:
            yield from iter(errs)
            return

        # we know the structure is valid at this point
        # so any child rule doesn't have to revalidate it
        value_validator = validator.evolve(
            context=validator.context.evolve(
                path=validator.context.path.descend(path=key)
            )
        )
        for _, rule in self.child_rules.items():
            if rule and hasattr(rule, "validate"):
                for err in rule.validate(value_validator, s, value, schema):
                    err.path.append("Fn::Sub")
                    err.rule = rule
                    yield err
