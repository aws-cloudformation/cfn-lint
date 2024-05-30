"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Required(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3003"
    shortdesc = "Required Resource properties are missing"
    description = "Make sure that Resources properties that are required exist"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#required"
    tags = ["resources", "properties", "required"]
