"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Cidr(CloudFormationLintRule):
    """Check if Cidr values are correct"""

    id = "E1024"
    shortdesc = "Cidr validation of parameters"
    description = "Making sure the function CIDR is a list with valid values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-cidr.html"
    tags = ["functions", "cidr"]
