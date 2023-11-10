"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.jsonschema.AwsType import AwsType as ParentAwsType


class AwsType(ParentAwsType):
    """Check if Resource Properties are correct"""

    id = "E3008"
    shortdesc = "Parent rule to validate values against AWS types"
    description = "Checks the types of resource property values"
    tags = ["resources", "ref", "getatt"]

    def __init__(self):
        super().__init__()

        self.child_rules = {
            "W3010": None,
            "E3510": None,
            "E3511": None,
        }

        self.types = {
            "AvailabilityZone": "W3010",
            "AvailabilityZones": "W3010",
            "IamIdentityPolicy": "E3510",
            "IamRoleArn": "E3511",
        }
