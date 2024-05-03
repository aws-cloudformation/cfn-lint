"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.MaxProperties import MaxProperties as ParentMaxProperties


class MaxProperties(ParentMaxProperties):
    """Check if maximum Mappings limit is exceeded"""

    id = "E7010"
    shortdesc = "Max number of properties for Mappings"
    description = (
        "Check the number of Mappings in the template is less than the upper limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["mappings", "limits"]

    def __init__(self) -> None:
        super().__init__("I7010")
