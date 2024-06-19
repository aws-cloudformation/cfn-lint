"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule  # pylint: disable=E0401


class CustomRule1(CloudFormationLintRule):
    """Def Rule"""

    id = "E9001"
    shortdesc = "Custom Rule 1"
    description = "Test Rule Description"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/"
    tags = ["resources"]
