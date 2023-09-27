"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class Configuration(CloudFormationLintRule):
    """Check if Conditions are configured correctly"""

    id = "E8001"
    shortdesc = "Conditions have appropriate properties"
    description = "Check if Conditions are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html"
    tags = ["conditions"]

    def condition(self, validator, tS, instance, schema):
        new_validator = validator.extend(
            validators={
                "type": cfn_type,
            },
            context=validator.context.evolve(
                functions=[
                    "Fn::And",
                    "Fn::Equals",
                    "Fn::Or",
                    "Fn::Not",
                    "Condition",
                ],
            ),
        )(schema={"type": "boolean"})

        for err in new_validator.iter_errors(instance):
            yield err
