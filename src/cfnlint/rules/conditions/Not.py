"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.other.functions
from cfnlint.rules.functions._BaseFn import BaseFn, SchemaDetails


class Not(BaseFn):
    """Check Not Condition Function Logic"""

    id = "E8005"
    shortdesc = "Check Fn::Not structure for validity"
    description = "Check Fn::Not is a list of one element"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-not"
    tags = ["functions", "not"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::Not",
            ("boolean",),
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.functions, "not.json"
            ),
        )
        self.fn_not = self.validate

    # if validator.context.path.path and validator.context.path.path[0] == "Rules":
    #        functions = list(FUNCTION_RULES)
