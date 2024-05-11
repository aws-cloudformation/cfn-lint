"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules._Rule import CloudFormationLintRule


class RuleError(CloudFormationLintRule):
    """Rule processing Error"""

    id = "E0002"
    shortdesc = "Error processing rule on the template"
    description = "Errors found when processing a rule on the template"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["base", "rule"]
