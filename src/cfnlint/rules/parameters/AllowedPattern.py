"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class AllowedPattern(CloudFormationLintRule):
    """Check if parameters have a valid value"""

    id = "W2031"
    shortdesc = "Check if parameters have a valid value based on an allowed pattern"
    description = "Check if parameters have a valid value in a pattern. The Parameter's allowed pattern is based on the usages in property (Ref)"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["parameters", "resources", "property", "allowed pattern"]
