"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Configuration(CloudFormationLintRule):
    """Check if Parameters are configured correctly"""

    id = "E2001"
    shortdesc = "Parameters have appropriate properties"
    description = "Making sure the parameters are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html"
    tags = ["parameters"]
