"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules import CloudFormationLintRule


class Condition(CloudFormationLintRule):
    """Check if Outputs have string values"""

    id = "E8007"
    shortdesc = "Conditions is properly configured with a boolean"
    description = "Validates that a condition is a boolean using appropriate functions"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html"
    tags = ["conditions"]

    def cfncondition(self, validator, tS, instance, schema):
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
