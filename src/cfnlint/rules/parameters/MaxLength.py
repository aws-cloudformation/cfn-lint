"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class MaxLength(CloudFormationLintRule):
    """Check if maximum Parameter value size limit is exceeded"""

    id = "E2012"
    shortdesc = "Parameter value limit not exceeded"
    description = (
        "Check if the size of Parameter values in the template is less than the upper"
        " limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["parameters", "limits"]
