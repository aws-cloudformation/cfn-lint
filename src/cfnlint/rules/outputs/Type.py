"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Type(CloudFormationLintRule):
    """Check if Outputs have the correct type"""

    id = "E6003"
    shortdesc = "Check the type of Outputs"
    description = "Validatoe the type of properties in the Outputs section"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]
