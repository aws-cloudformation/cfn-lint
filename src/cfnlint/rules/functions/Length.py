"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Length(CloudFormationLintRule):
    """Check if Length values are correct"""

    id = "E1030"
    shortdesc = "Length validation of parameters"
    description = "Making sure Fn::Length is configured correctly"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-length.html"
    tags = ["functions", "length"]
