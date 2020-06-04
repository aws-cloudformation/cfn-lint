"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import alphanumeric_name


class Name(CloudFormationLintRule):
    """Check if Parameters are named correctly"""
    id = 'E2003'
    shortdesc = 'Parameters have appropriate names'
    description = 'Check if Parameters are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html#parameters-section-structure-requirements'
    tags = ['parameters']

    def match(self, cfn):
        return alphanumeric_name(cfn, 'Parameters')
