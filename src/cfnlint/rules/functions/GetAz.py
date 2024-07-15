"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import REGIONS
from cfnlint.jsonschema import Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class GetAz(BaseFn):
    """Check if GetAz values are correct"""

    id = "E1015"
    shortdesc = "GetAz validation of parameters"
    description = "Making sure the GetAz function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getavailabilityzones.html"
    tags = ["functions", "getaz"]

    def __init__(self) -> None:
        super().__init__("Fn::GetAZs", ("array",), ("Ref",), resolved_rule="W1036")
        self.fn_getazs = self.validate

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        return {
            "type": ["string"],
            "enum": [""] + REGIONS,
        }
