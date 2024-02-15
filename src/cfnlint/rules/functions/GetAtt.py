"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Dict, List

import regex as re

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules.functions._BaseFn import BaseFn, all_types


class GetAtt(BaseFn):
    """Check if GetAtt values are correct"""

    id = "E1010"
    shortdesc = "GetAtt validation of parameters"
    description = (
        "Validates that GetAtt parameters are to valid resources and properties of"
        " those resources"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "getatt"]

    def __init__(self) -> None:
        super().__init__("Fn::GetAtt", all_types)

    def schema(self, validator, instance) -> Dict[str, Any]:
        resource_functions = []
        if validator.context.transforms.has_language_extensions_transform():
            resource_functions = ["Ref"]

        return {
            "type": ["string", "array"],
            "minItems": 2,
            "maxItems": 2,
            "fn_items": [
                {
                    "functions": resource_functions,
                    "schema": {
                        "type": ["string"],
                    },
                },
                {
                    "functions": ["Ref"],
                    "schema": {
                        "type": ["string"],
                    },
                },
            ],
        }

    def fn_getatt(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        errs = list(super().validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)
            return

        key, value = self.key_value(instance)
        paths: List[int | None] = [0, 1]
        if validator.is_type(value, "string"):
            paths = [None, None]
            value = value.split(".", 1)

        def iter_errors(type: str) -> ValidationResult:
            value: Any = None
            if type == "string":
                value = ""
            elif type == "number":
                value = 1.0
            elif type == "integer":
                value = 1
            elif type == "boolean":
                value = True
            elif type == "array":
                value = []
            elif type == "object":
                value = {}
            else:
                return

            for err in evolved.iter_errors(value):
                err.message = err.message.replace(f"{value!r}", f"{instance!r}")
                err.validator = self.fn.py
                err.path = deque([key])
                yield err

        for resource_name, resource_name_validator, _ in validator.resolve_value(
            value[0]
        ):
            for err in self.fix_errors(
                resource_name_validator.descend(
                    resource_name,
                    {"enum": list(validator.context.resources.keys())},
                    key,
                )
            ):
                err.path.append(paths[0])
                if err.instance != value[0]:
                    err.message = err.message + f" when {value[0]!r} is resolved"
                yield err
                break
            else:
                for attribute_name, _, _ in validator.resolve_value(value[1]):
                    if all(
                        not (bool(re.fullmatch(each, attribute_name)))
                        for each in validator.context.resources[resource_name].get_atts
                    ):
                        err = ValidationError(
                            (
                                f"{attribute_name!r} is not one of "
                                f"{validator.context.resources[resource_name].get_atts!r}"
                            ),
                            validator=self.fn.py,
                            path=deque([self.fn.name, 1]),
                        )
                        if attribute_name != value[1]:
                            err.message = (
                                err.message + f" when {value[1]!r} is resolved"
                            )
                        yield err
                        break
                else:
                    # because of the complexities of schemas ($ref, anyOf, allOf, etc.)
                    # we will simplify the validator to just have a type check
                    # then we will provide a simple value to represent the type from the
                    # getAtt
                    evolved = validator.evolve(schema=s)  # type: ignore
                    evolved.validators = {  # type: ignore
                        "type": validator.validators.get("type"),  # type: ignore
                    }

                    types = ensure_list(
                        validator.context.resources[resource_name]
                        .get_atts[attribute_name]
                        .type
                    )

                    # validate all possible types.
                    # We will only alert when all types fail
                    type_err_ct = 0
                    all_errs = []
                    for type in types:
                        errs = list(iter_errors(type))
                        if errs:
                            type_err_ct += 1
                            all_errs.extend(errs)

                    if type_err_ct == len(types):
                        yield from errs
