"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.functions
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, SchemaDetails


class Condition(BaseFn):
    """Check And Condition Function Logic"""

    id = "E8007"
    shortdesc = "Check Condition structure for validity"
    description = "Check Condition has a value of another condition"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-and"
    tags = ["functions", "condition"]

    def __init__(self) -> None:
        super().__init__(
            "Condition",
            ("boolean",),
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.functions, "condition.json"
            ),
        )
        self.condition = self.validate

    def validate(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        # Stamp these errors with this rule before they bubble up. The
        # enclosing rules (Fn::And, Fn::Or, Fn::Not, and the Conditions
        # section rule) rewrite the error validator to their own id, so
        # without the stamp an undefined Condition name is reported as
        # E8004, E8005, E8006, or E8001 and E8007 can neither select nor
        # suppress it. The stamp survives both rewrites: fix_errors only
        # touches the validator, and the error cleaners only assign a rule
        # when none is set.
        for err in super().validate(validator, s, instance, schema):
            if err.rule is None:
                err.rule = self
            yield err
