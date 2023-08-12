"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class ImportValue(CloudFormationLintRule):
    """Check if ImportValue values are correct"""

    id = "E1016"
    shortdesc = "ImportValue validation of parameters"
    description = "Making sure the ImportValue function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-importvalue.html"
    tags = ["functions", "importvalue"]
