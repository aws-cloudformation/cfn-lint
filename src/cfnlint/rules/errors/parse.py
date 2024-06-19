"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules._rule import CloudFormationLintRule


class ParseError(CloudFormationLintRule):
    """Parse Lint Rule"""

    id = "E0000"
    shortdesc = "Parsing error found when parsing the template"
    description = "Checks for JSON/YAML formatting errors in your template"
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["base"]
