"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class ApproachingMaxLength(CloudFormationLintRule):
    """Check maximum Mapping name size limit"""

    id = "I7002"
    shortdesc = "Mapping name limit"
    description = (
        "Check the size of Mapping names in the template is approaching the upper limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["mappings", "limits"]
