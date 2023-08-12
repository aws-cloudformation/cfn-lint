"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Select(CloudFormationLintRule):
    """Check if Select values are correct"""

    id = "E1017"
    shortdesc = "Select validation of parameters"
    description = "Making sure the Select function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html"
    tags = ["functions", "select"]
    supported_functions = [
        "Fn::FindInMap",
        "Fn::GetAtt",
        "Fn::GetAZs",
        "Fn::If",
        "Fn::Split",
        "Fn::Cidr",
        "Fn::Select",  # issue: 2895
        "Ref",
    ]
