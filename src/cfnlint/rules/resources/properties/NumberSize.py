"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class NumberSize(CloudFormationLintRule):
    """Check if a Number has a length within the limit"""

    id = "E3034"
    shortdesc = "Check if a number is between min and max"
    description = (
        "Check numbers (integers and floats) for its value being between the minimum"
        " and maximum"
    )
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "number", "size"]
