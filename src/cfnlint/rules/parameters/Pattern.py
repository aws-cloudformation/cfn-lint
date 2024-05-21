"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Pattern(CloudFormationLintRule):
    """Check if maximum Parameter name size limit is exceeded"""

    id = "E2003"
    shortdesc = "Parameters have appropriate names"
    description = "Check if Parameters are properly named (A-Za-z0-9)"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["parameters", "name"]
