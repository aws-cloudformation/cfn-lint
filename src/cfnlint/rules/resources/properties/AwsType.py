"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class AwsType(CloudFormationLintRule):
    """Check if Resource Properties are correct"""

    id = "E3008"
    shortdesc = "Parent rule to validate values against AWS types"
    description = "Checks the types of resource property values"
    tags = ["resources", "ref", "getatt"]

    def __init__(self):
        super().__init__()
        self.cfn = None

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

    def initialize(self, cfn):
        self.cfn = cfn
        return super().initialize(cfn)

    # pylint: disable=unused-argument
    def awsType(self, validator, uI, instance, schema):
        rule = self.child_rules.get(self.types.get(uI, ""))
        if not rule:
            return

        if hasattr(rule, uI.lower()) and callable(getattr(rule, uI.lower())):
            validate = getattr(rule, uI.lower())
            yield from validate(validator, uI, instance, schema)
