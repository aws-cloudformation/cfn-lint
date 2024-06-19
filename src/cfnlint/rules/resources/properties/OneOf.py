"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class OneOf(CloudFormationLintRule):
    """Check Properties Resource Configuration"""

    id = "E3018"
    shortdesc = "Check Properties that need only one of a list of properties"
    description = (
        "Making sure CloudFormation properties "
        + "that require only one property from a list. "
        + "One has to be specified."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources"]
