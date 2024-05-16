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

        for err in validator.descend(
            instance=value[0],
            schema={"enum": list(validator.context.conditions.keys())},
            path=0,
        ):
            err.path.appendleft(key)
            err.rule = self
            err.validator = self.fn.py
            yield err

        for i in [1, 2]:
            for err in validator.descend(instance=value[i], schema=s, path=i):
                err.path.appendleft(key)
                yield err
