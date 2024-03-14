"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class LimitNumber(CloudFormationLintRule):
    """Check maximum Parameter limit"""

    id = "I2010"
    shortdesc = "Parameter limit"
    description = (
        "Check the number of Parameters in the template is approaching the upper limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["parameters", "limits"]
