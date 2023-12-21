"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class Split(CloudFormationLintRule):
    """Check if Split values are correct"""

    id = "E1018"
    shortdesc = "Split validation of parameters"
    description = "Making sure the split function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-split.html"
    tags = ["functions", "split"]
