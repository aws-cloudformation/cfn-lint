"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import PSEUDOPARAMS, VALID_PARAMETER_TYPES_LIST
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class Sub(CloudFormationLintRule):
    """Check if Sub values are correct"""

    id = "E1019"
    shortdesc = "Sub validation of parameters"
    description = "Making sure the sub function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub"]
