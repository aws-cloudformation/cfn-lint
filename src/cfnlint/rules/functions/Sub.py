"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any, Dict

import regex as re

from cfnlint.context.context import Parameter
from cfnlint.helpers import REGEX_SUB_PARAMETERS
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.jsonschema._utils import ensure_list
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
                    "functions": [
                        "Fn::Base64",
                        "Fn::FindInMap",
                        "Fn::GetAZs",
                        "Fn::GetAtt",
                        "Fn::If",
                        "Fn::ImportValue",
                        "Fn::Join",
                        "Fn::Select",
                        "Fn::Sub",
                        "Ref",
                        "Fn::ToJsonString",
                    ],
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

    def _validate_string(self, validator: Validator, instance: Any) -> ValidationResult:
        params = re.findall(REGEX_SUB_PARAMETERS, instance)
        for param in params:
            param = param.strip()
            valid_params = []
            if "." in param:
                [name, attr] = param.split(".", 1)
                if name in validator.context.resources:
                    if attr in validator.context.resources[name].get_atts:
                        tS = ensure_list(
                            validator.context.resources[name].get_atts[attr].type
                        )
                        if not any(type in tS for type in self.sub_parameter_types):
                            reprs = ", ".join(
                                repr(type) for type in self.sub_parameter_types
                            )
                            yield ValidationError(
                                message=f"{param!r} is not of type {reprs}",
                                validator=self.fn.py,
                                path=deque([self.fn.name]),
                            )
                            continue
                    valid_params = [
                        f"{name}.{attr}"
                        for attr in list(
                            validator.context.resources[name].get_atts.keys()
                        )
                    ]
                else:
                    valid_params = list(validator.context.resources.keys())
            else:
                valid_params = validator.context.refs

            if param not in valid_params:
                yield ValidationError(
                    message=f"{param!r} is not one of {valid_params!r}",
                    validator=self.fn.py,
                    path=deque([self.fn.name]),
                )

    def fn_sub(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield from super().validate(validator, s, instance, schema)

        _, value = self.key_value(instance)
        if validator.is_type(value, "array"):
            if len(value) != 2:
                return
            if not validator.is_type(value[1], "object"):
                return

            validator_string = validator.evolve(
                context=validator.context.evolve(
                    ref_values=dict.fromkeys(
                        list(value[1].keys()), Parameter({"Type": "String"})
                    ),
                )
            )
            value = value[0]
        elif validator.is_type(value, "string"):
            validator_string = validator
        else:
            return

        errs = list(self._validate_string(validator_string, value))
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
