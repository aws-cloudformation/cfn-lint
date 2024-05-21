"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.PropertyNames import PropertyNames as ParentPropertyNames


class PropertyNames(ParentPropertyNames):
    """Check for string length in Outputs"""

    id = "E6011"
    shortdesc = "Check property names in Outputs"
    description = "Validate property names are property configured in Outputs"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs", "limits"]

    def __init__(self) -> None:
        super().__init__("I6011")
