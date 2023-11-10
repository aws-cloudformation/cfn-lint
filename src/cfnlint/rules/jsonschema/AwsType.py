"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class AwsType(CloudFormationLintRule):
    """Check Conditions awsType values are correct"""

    # pylint: disable=unused-argument
    def awsType(self, validator, uI, instance, schema):
        rule = self.child_rules.get(self.types.get(uI, ""))
        if not rule:
            return

        if hasattr(rule, uI.lower()) and callable(getattr(rule, uI.lower())):
            validate = getattr(rule, uI.lower())
            yield from validate(validator, uI, instance, schema)
