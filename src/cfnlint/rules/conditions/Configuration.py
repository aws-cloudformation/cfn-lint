"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class Configuration(CloudFormationLintRule):
    """Check if Conditions are configured correctly"""

    id = "E8001"
    shortdesc = "Conditions have appropriate properties"
    description = "Check if Conditions are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html"
    tags = ["conditions"]

    def condition(self, validator, tS, instance, schema):
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=[
                    "Fn::And",
                    "Fn::Equals",
                    "Fn::Or",
                    "Fn::Not",
                    "Condition",
                ],
            )
        )

        for err in validator.descend(instance, {"type": "boolean"}):
            yield err
