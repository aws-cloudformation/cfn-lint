"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class AtLeastOne(CloudFormationLintRule):
    """Check Properties Resource Configuration"""

    id = "E2522"
    shortdesc = "Check Properties that need at least one of a list of properties"
    description = (
        "Making sure CloudFormation properties "
        + "that require at least one property from a list. "
        + "More than one can be included."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]
