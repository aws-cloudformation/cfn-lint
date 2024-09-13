"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class RequiredOr(CloudFormationLintRule):
    id = "E3058"
    shortdesc = "Validate at least one of the properties are required"
    description = "Make sure at least one of the resource properties are included"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#requiredor"
    tags = ["resources"]
