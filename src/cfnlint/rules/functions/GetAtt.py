"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class GetAtt(CloudFormationLintRule):
    """Check if GetAtt values are correct"""

    id = "E1010"
    shortdesc = "GetAtt validation of parameters"
    description = (
        "Validates that GetAtt parameters are to valid resources and properties of"
        " those resources"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "getatt"]
