"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.PropertyNames import PropertyNames as ParentPropertyNames


class PropertyNames(ParentPropertyNames):
    """Check if maximum Parameter name size limit is exceeded"""

    id = "E2003"
    shortdesc = "Check property names in Parameters"
    description = "Validate property names are property configured in Parameters"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["parameters", "limits"]

    def __init__(self) -> None:
        super().__init__("I2003")
