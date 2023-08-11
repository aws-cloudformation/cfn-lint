"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Union

from cfnlint.helpers import VALID_PARAMETER_TYPES_LIST
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import GetAtts, Template


class Join(CloudFormationLintRule):
    """Check if Join values are correct"""

    id = "E1022"
    shortdesc = "Join validation of parameters"
    description = "Making sure the join function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-join.html"
    tags = ["functions", "join"]
