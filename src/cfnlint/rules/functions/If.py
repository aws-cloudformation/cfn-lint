"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.context.conditions.exceptions import Unsatisfiable
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
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
        self.child_rules["W1028"] = None

    def schema(self, validator, instance) -> dict[str, Any]:
        return {
            "type": ["array"],
            "minItems": 3,
            "maxItems": 3,
            "fn_items": [
                {
                    "functions": [],
                    "schema": {
                        "type": ["string"],
                        "enum": list(validator.context.conditions.conditions.keys()),
                    },
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
                        value,
                        self.schema(validator, instance),
                        path=key,
                    )
                )
            )
        )

        if errs:
            yield from iter(errs)
            return

        for i in [1, 2]:
            # we pass through the functions for the paths down
            # the second and third element of the if
            try:
                element_validator = validator.evolve(
                    context=validator.context.evolve(
                        path=validator.context.path.descend(
                            path=key,
                        ),
                        conditions=validator.context.conditions.evolve(
                            {value[0]: True if i == 1 else False}
                        ),
                    )
                )
                for err in element_validator.descend(
                    instance=value[i], schema=s, path=i
                ):
                    err.path.appendleft(key)
                    yield err
            except Unsatisfiable as e:
                yield ValidationError(
                    f"{[key, i]!r} is not reachable. {e.message}",
                    path=deque([key, i]),
                    rule=self.child_rules["W1028"],
                )
                element_validator = validator.evolve(
                    context=validator.context.evolve(
                        path=validator.context.path.descend(
                            path=key,
                        ),
                    )
                )
                for err in element_validator.descend(
                    instance=value[i], schema=s, path=i
                ):
                    err.path.appendleft(key)
                    yield err
