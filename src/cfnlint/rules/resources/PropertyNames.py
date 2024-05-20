"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.PropertyNames import PropertyNames as ParentPropertyNames


class MaxLength(ParentPropertyNames):
    """Check if maximum Resource name size limit is exceeded"""

    id = "E3011"
    shortdesc = "Check property names in Resources"
    description = "Validate property names are property configured in Resources"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["resources", "limits"]

    def __init__(self) -> None:
        super().__init__(
            approaching_limit_rule="I3012",
        )
