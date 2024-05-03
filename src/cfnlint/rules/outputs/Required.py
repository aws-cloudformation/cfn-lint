"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Required(CloudFormationLintRule):
    """Check if Outputs have required properties"""

    id = "E6002"
    shortdesc = "Outputs have required properties"
    description = "Making sure the outputs have required properties"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]
