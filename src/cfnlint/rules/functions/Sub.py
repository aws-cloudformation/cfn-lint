"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any, Dict

import regex as re

from cfnlint.helpers import REGEX_SUB_PARAMETERS
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
        super().__init__("Fn::Sub", ("string",))
        self.sub_parameter_types = ["string", "integer", "number", "boolean"]
        self.child_rules = {
            "W1019": None,
            "W1020": None,
        }
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

    def schema(self, validator: Validator, instance: Any) -> Dict[str, Any]:
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
        self, validator: Validator, key: str, instance: Any
    ) -> ValidationResult:
        params = re.findall(REGEX_SUB_PARAMETERS, instance)
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=self._functions,
                path=validator.context.path.descend(
                    path=key,
                    cfn_path=key,
                ),
            ),
        )
        for param in params:
            param = param.strip()
            if "." in param:
                for err in validator.descend(
                    instance={"Fn::GetAtt": param},
                    schema={"type": ["string"]},
                    path=key,
                ):
                    yield self._clean_error(err, {"Fn::GetAtt": param}, param)
            else:
                for err in validator.descend(
                    instance={"Ref": param},
                    schema={"type": ["string"]},
                    path=key,
                ):
                    yield self._clean_error(err, {"Ref": param}, param)

    def fn_sub(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        validator = validator.evolve(
            context=validator.context.evolve(strict_types=True)
        )
        yield from super().validate(validator, s, instance, schema)

        key, value = self.key_value(instance)
        if validator.is_type(value, "array"):
            if len(value) != 2:
                return
            if not validator.is_type(value[1], "object"):
                return

            validator_string = validator.evolve(
                context=validator.context.evolve(ref_values=value[1])
            )
            value = value[0]
        elif validator.is_type(value, "string"):
            validator_string = validator
        else:
            return

        errs = list(self._validate_string(validator_string, key, value))
        if errs:
            yield from iter(errs)
            return

        # we know the structure is valid at this point
        # so any child rule doesn't have to revalidate it
        for _, rule in self.child_rules.items():
            if rule:
                for err in rule.validate(validator, s, instance.get("Fn::Sub"), schema):
                    err.path.append("Fn::Sub")
                    err.rule = rule
                    yield err
