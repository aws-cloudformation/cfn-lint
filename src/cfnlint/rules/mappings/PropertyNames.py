"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.PropertyNames import PropertyNames as ParentPropertyNames


class PropertyNames(ParentPropertyNames):
    """Check for string length in Mappings"""

    id = "E7002"
    shortdesc = "Check property names in Mappings"
    description = "Validate property names are property configured in Mappings"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html"
    tags = ["mappings", "limits"]

    def __init__(self) -> None:
        super().__init__("I7002")
