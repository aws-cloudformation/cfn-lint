"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.jsonschema.PropertyNames import PropertyNames as ParentPropertyNames


class PropertyNames(ParentPropertyNames):
    """Check for string length in Outputs"""

    id = "E6004"
    shortdesc = "Check the max length of strings in Outputs"
    description = "Check the size of Outputs strings are within the max length"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs", "limits"]

    def __init__(self) -> None:
        super().__init__("I6011")
