"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class GetAz(CloudFormationLintRule):
    """Check if GetAz values are correct"""

    id = "E1015"
    shortdesc = "GetAz validation of parameters"
    description = "Making sure the GetAz function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getavailabilityzones.html"
    tags = ["functions", "getaz"]
