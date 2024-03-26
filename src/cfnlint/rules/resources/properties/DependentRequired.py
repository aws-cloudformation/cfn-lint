"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class DependentExcluded(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3021"
    shortdesc = (
        "Validate that when a property is specified that "
        "other properties should be included"
    )
    description = (
        "When certain properties are specified it results "
        "in other properties to be required"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#pr"
    tags = ["resources"]
