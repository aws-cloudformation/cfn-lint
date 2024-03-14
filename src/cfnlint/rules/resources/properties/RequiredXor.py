"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class RequiredXor(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3014"
    shortdesc = "Validate only one of a set of required properties are specified"
    description = "Making sure that Resources properties that are required exist"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#required"
    tags = ["resources"]
