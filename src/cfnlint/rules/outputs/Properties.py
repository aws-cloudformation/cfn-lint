"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class Properties(CloudFormationLintRule):
    """Check if Outputs have string values"""

    id = "E6001"
    shortdesc = "Check the properties of Outputs"
    description = "Validate the property structure for outputs"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]
