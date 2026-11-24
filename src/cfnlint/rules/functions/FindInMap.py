"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import (
    BaseFn,
    _has_schema_constraints,
    singular_types,
)


class FindInMap(BaseFn):
    """Check if FindInMap values are correct"""

    id = "E1011"
    shortdesc = "FindInMap validation of configuration"
    description = "Making sure the function is a list of appropriate config"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-findinmap.html"
    tags = ["functions", "findinmap"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::FindInMap",
            ("array",) + singular_types,
            resolved_rule="W1034",
        )
        self.fn_findinmap = self.validate

    def resolve(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        # BaseFn.resolve skips resolution entirely when the target schema
        # carries no constraining keyword, which hides definite lookup
        # failures (unknown map name, unknown top-level key, unknown
        # second-level key) in unconstrained positions such as Condition
        # operands, Fn::Join items, Fn::Sub variables, and unconstrained
        # properties. Those failures reject the template at
        # ValidateTemplate no matter where the lookup sits, so run
        # resolution for its errors even when there is no resolved value
        # to validate. Value validation still only runs when constraints
        # exist, so unconstrained positions gain no new value findings.
        if _has_schema_constraints(s):
            yield from super().resolve(validator, s, instance, schema)
            return

        validator = validator.evolve(
            context=validator.context.evolve(
                strict_types=False,
            ),
        )
        for _, v, resolve_err in validator.resolve_value(instance):
            if resolve_err:
                # A resolution error against a value that only exists
                # because of a parameter's Default (which a deployer can
                # override at deployment time) is not a definite failure,
                # so we don't report it. Hardcoded values are validated.
                if v.context.is_resolved_from_parameters:
                    continue
                yield from self.fix_errors(iter([resolve_err]))
                continue
            if not v.context.is_resolved_from_parameters:
                return
