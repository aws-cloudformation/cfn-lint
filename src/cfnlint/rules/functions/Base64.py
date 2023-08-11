"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class Base64(CloudFormationLintRule):
    """Check if Base64 values are correct"""

    id = "E1021"
    shortdesc = "Base64 validation of parameters"
    description = "Making sure the Base64 function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-base64.html"
    tags = ["functions", "base64"]
