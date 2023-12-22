"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class ApproachingMaxLength(CloudFormationLintRule):
    """Check maximum Parameter name size limit"""

    id = "I2012"
    shortdesc = "Parameter name limit"
    description = (
        "Check the size of Parameter names in the template is approaching the upper"
        " limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["parameters", "limits"]
