"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.functions
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions._BaseFn import BaseFn, SchemaDetails


class And(BaseFn):
    """Check And Condition Function Logic"""

    id = "E8004"
    shortdesc = "Check Fn::And structure for validity"
    description = "Check Fn::And is a list of two to ten elements"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-and"
    tags = ["functions", "and"]

    def message(self, instance: Any, err: ValidationError) -> str:
        if err.schema_path and err.schema_path[-1] == "not":
            return (
                f"{err.instance!r} is not a valid Fn::And operand; "
                "operands must be a condition or a condition function"
            )
        return err.message

    def __init__(self) -> None:
        super().__init__(
            "Fn::And",
            ("boolean",),
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.functions, "or.json"
            ),
        )
        self.fn_and = self.validate
