"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.other.functions
from cfnlint.rules.functions._BaseFn import BaseFn, SchemaDetails


class Or(BaseFn):
    """Check Or Condition Function Logic"""

    id = "E8006"
    shortdesc = "Check Fn::Or structure for validity"
    description = "Check Fn::Or is a list of two elements"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-or"
    tags = ["functions", "or"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::Or",
            ("boolean",),
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.functions, "or.json"
            ),
        )
        self.fn_or = self.validate
