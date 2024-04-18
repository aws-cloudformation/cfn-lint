"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class ArrayLength(CloudFormationLintRule):
    """Check if List has a size within the limit"""

    id = "E3032"
    shortdesc = "Check if a array has between min and max number of values specified"
    description = (
        "Check array for the number of items in the list to validate they are between"
        " the minimum and maximum"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#arraylength"
    tags = ["resources", "property", "array", "length"]
