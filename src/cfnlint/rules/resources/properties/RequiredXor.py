"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class RequiredXor(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3014"
    shortdesc = "Validate only one of a set of required properties are specified"
    description = (
        "Make sure that Resources properties that are required exist. "
        "Along with other properties not being specified"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#requiredxor"
    tags = ["resources"]
