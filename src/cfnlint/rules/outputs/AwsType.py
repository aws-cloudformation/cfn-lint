"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class AwsType(CloudFormationLintRule):
    """Check if Resource Properties are correct"""

    id = "E6100"
    shortdesc = "Parent rule to validate values against AWS types"
    description = "Checks the types of resource property values"
    tags = ["outputs"]

    def __init__(self):
        super().__init__()
        self.cfn = None

        self.child_rules = {
            "E6101": None,
            "E6102": None,
        }

        self.types = {
            "outputValue": "E6101",
            "outputExport": "E6102",
        }

    # pylint: disable=unused-argument
    def awsType(self, validator, uI, instance, schema):
        rule = self.child_rules.get(self.types.get(uI, ""))
        if not rule:
            return

        if hasattr(rule, uI.lower()) and callable(getattr(rule, uI.lower())):
            validate = getattr(rule, uI.lower())
            yield from validate(validator, uI, instance, schema)
