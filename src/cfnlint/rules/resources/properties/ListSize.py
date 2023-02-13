"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class ListSize(CloudFormationLintRule):
    """Check if List has a size within the limit"""

    id = "E3032"
    shortdesc = "Check if a list has between min and max number of values specified"
    description = "Check lists for the number of items in the list to validate they are between the minimum and maximum"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "list", "size"]
