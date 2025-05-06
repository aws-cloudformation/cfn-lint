"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.functions._BaseFn import BaseFn


class Cidr(BaseFn):
    """Check if Cidr values are correct"""

    id = "E1024"
    shortdesc = "Cidr validation of parameters"
    description = "Making sure the function CIDR is a list with valid values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-cidr.html"
    tags = ["functions", "cidr"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::Cidr",
            ("array",),
            None,
        )
        self.fn_cidr = self.validate
