"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.other.functions
from cfnlint.rules.functions._BaseFn import BaseFn, SchemaDetails, all_types


class Select(BaseFn):
    """Check if Select values are correct"""

    id = "E1017"
    shortdesc = "Select validation of parameters"
    description = "Making sure the Select function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html"
    tags = ["functions", "select"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::Select",
            all_types,
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.functions, "select.json"
            ),
            resolved_rule="W1035",
        )
        self.fn_select = self.validate
