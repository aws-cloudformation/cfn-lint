"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules._rule import CloudFormationLintRule


class TransformError(CloudFormationLintRule):
    """Transform Lint Rule"""

    id = "E0001"
    shortdesc = "Error found when transforming the template"
    description = "Errors found when performing transformation on the template"
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["base", "transform"]
