"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.PropertyNames import PropertyNames as ParentPropertyNames


class PropertyNames(ParentPropertyNames):
    id = "E2011"
    shortdesc = "Validate the name for a parameter"
    description = (
        "Validate the name of a parameter with special handling "
        "of the max length length"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["parameters", "limits"]

    # by bundling under propertyNames we can include one rule for all property
    # name validation

    def __init__(self) -> None:
        super().__init__("I2011")
