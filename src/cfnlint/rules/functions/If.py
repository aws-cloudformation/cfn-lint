"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Dict

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, all_types


class If(BaseFn):
    """Check if Condition exists"""

    id = "E1028"
    shortdesc = "Check Fn::If structure for validity"
    description = "Check Fn::If to make sure its valid.  Condition has to be a string."
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-if"
    tags = ["functions", "if"]

    def __init__(self) -> None:
        super().__init__("Fn::If", all_types)

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["array"],
            "minItems": 3,
            "maxItems": 3,
            "fn_items": [
                {
                    "schema": {
                        "type": ["string"],
                    }
                },
            ],
        }

    def fn_if(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        # validate this function will return the correct type
        errs = list(self.validate_fn_output_types(validator, s, instance))

        key, value = self.key_value(instance)
        errs.extend(
            list(
                self.fix_errors(
                    self.validator(validator).descend(
                        value, self.schema(validator, instance), path=key
                    )
                )
            )
        )

        if errs:
            yield from iter(errs)
            return

        found_errs = False
        for err in validator.descend(value[0], {"awsType": "CfnCondition"}, 0):
            err.path.appendleft(key)
            yield err
            found_errs = True

        for err in validator.descend(value[1], s, 1):
            err.path.appendleft(key)
            yield err
            found_errs = True
        for err in validator.descend(value[2], s, 2):
            err.path.appendleft(key)
            yield err
            found_errs = True

        if not found_errs:
            yield from self.resolve(validator, s, instance, schema)

    def resolve(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        key, _ = self.key_value(instance)
        for value, v, _ in validator.resolve_value(instance):
            for err in v.descend(value, s, key):
                err.path.extend(v.context.value_path)
                yield err
