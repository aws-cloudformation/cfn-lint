"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.jsonschema.AwsType import AwsType as ParentAwsType


class AwsType(ParentAwsType):
    """Check Conditions awsType values are correct"""

    id = "E8100"
    shortdesc = "Parent rule to validate values against AWS types"
    description = "Checks the types of resource property values"
    tags = ["conditions"]

    def __init__(self):
        super().__init__()

        self.child_rules = {
            "E8001": None,
        }

        self.types = {
            "condition": "E8001",
        }
