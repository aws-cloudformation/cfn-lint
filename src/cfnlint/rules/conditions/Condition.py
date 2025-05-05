"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.other.functions
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
