"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.MaxLength import MaxLength as ParentMaxLength


class MaxLength(ParentMaxLength):
    """Check if Outputs strings are less than the max length"""

    id = "E6011"
    shortdesc = "Check the max length of strings in Outputs"
    description = "Validate the the length of strings in Outputs doesn't exceed the max"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def __init__(self) -> None:
        super().__init__("I6011")
