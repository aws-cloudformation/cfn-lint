"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class UniqueItemsAllowed(CloudFormationLintRule):
    """Check if duplicates exist in a List"""

    id = "I3037"
    shortdesc = "Check if a list that allows duplicates has any duplicates"
    description = (
        "Certain lists support duplicate items."
        "Provide an alert when list of strings or numbers have repeats."
    )
    source_url = (
        "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/rules.md#rules-1"
    )
    tags = ["resources", "property", "list"]

    def __init__(self):
        super().__init__()
        self.exceptions = ["Command"]
