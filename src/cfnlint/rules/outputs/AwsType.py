"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.jsonschema.AwsType import AwsType as ParentAwsType


class AwsType(ParentAwsType):
    """Check if Resource Properties are correct"""

    id = "E6100"
    shortdesc = "Parent rule to validate values against AWS types"
    description = "Checks the types of resource property values"
    tags = ["outputs"]

    def __init__(self):
        super().__init__()

        self.child_rules = {
            "E6101": None,
            "E6102": None,
        }

        self.types = {
            "outputValue": "E6101",
            "outputExport": "E6102",
        }
