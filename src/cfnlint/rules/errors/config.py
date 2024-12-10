"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules._rule import CloudFormationLintRule


class ConfigError(CloudFormationLintRule):

    id = "E0003"
    shortdesc = "Error with cfn-lint configuration"
    description = "Error as a result of the cfn-lint configuration"
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["base", "rule"]
