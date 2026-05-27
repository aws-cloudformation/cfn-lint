"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class MaxUniqueItems(CloudFormationLintRule):
    """Check if a list has too many unique values"""

    id = "E3065"
    shortdesc = "Check if a list has more unique values than allowed"
    description = (
        "Some lists have a maximum number of unique items allowed. "
        "Validate that the number of unique items does not exceed the limit."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#maxuniqueitems"
    tags = ["resources", "property", "array", "length"]
