"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.functions
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions._BaseFn import BaseFn, SchemaDetails


class Or(BaseFn):
    """Check Or Condition Function Logic"""

    id = "E8006"
    shortdesc = "Check Fn::Or structure for validity"
    description = "Check Fn::Or is a list of two to ten elements"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-or"
    tags = ["functions", "or"]

    def message(self, instance: Any, err: ValidationError) -> str:
        if err.schema_path and err.schema_path[-1] == "not":
            return (
                f"{err.instance!r} is not a valid Fn::Or operand; "
                "operands must be a condition or a condition function"
            )
        return err.message

    def __init__(self) -> None:
        super().__init__(
            "Fn::Or",
            ("boolean",),
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.functions, "or.json"
            ),
        )
        self.fn_or = self.validate
