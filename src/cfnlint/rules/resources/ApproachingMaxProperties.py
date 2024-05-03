"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class ApproachingMaxProperties(CloudFormationLintRule):
    """Check maximum Resource limit"""

    id = "I3010"
    shortdesc = "Resource limit"
    description = (
        "Check the number of Resources in the template is approaching the upper limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["resources", "limits"]
