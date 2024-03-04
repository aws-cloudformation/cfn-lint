"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class DependentExcluded(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3023"
    shortdesc = (
        "Validate that when a property is specified another property should be excluded"
    )
    description = (
        "When certain properties are specified other properties should not be included"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md"
    tags = ["resources"]
