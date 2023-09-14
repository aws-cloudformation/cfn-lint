"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import FUNCTIONS
from cfnlint.rules import CloudFormationLintRule


class Condition(CloudFormationLintRule):
    """Check if Outputs have string values"""

    id = "E8007"
    shortdesc = "Conditions is properly configured with a boolean"
    description = "Validates that a condition is a boolean using appropriate functions"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html"
    tags = ["conditions"]
