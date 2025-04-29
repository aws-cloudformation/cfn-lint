"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.other.functions
from cfnlint.helpers import FUNCTIONS_SINGLE
from cfnlint.rules.functions._BaseFn import BaseFn, SchemaDetails


class Base64(BaseFn):
    """Check if Base64 values are correct"""

    id = "E1021"
    shortdesc = "Base64 validation of parameters"
    description = "Making sure the Base64 function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-base64.html"
    tags = ["functions", "base64"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::Base64",
            ("string",),
            tuple(FUNCTIONS_SINGLE),
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.functions, "base64.json"
            ),
        )
        self.fn_base64 = self.validate
