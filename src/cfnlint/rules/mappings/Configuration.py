"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class Configuration(CloudFormationLintRule):
    """Check if Mappings are configured correctly"""

    id = "E7001"
    shortdesc = "Mappings are appropriately configured"
    description = "Check if Mappings are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html"
    tags = ["mappings"]
