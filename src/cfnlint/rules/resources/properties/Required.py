"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class Required(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3003"
    shortdesc = "Required Resource properties are missing"
    description = "Making sure that Resources properties that are required exist"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#required"
    tags = ["resources"]
