"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import alphanumeric_name


class Name(CloudFormationLintRule):
    """Check if Resources are named correctly"""
    id = 'E3006'
    shortdesc = 'Resources have appropriate names'
    description = 'Check if Resources are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resources-section-structure.html#resources-section-structure-logicalid'
    tags = ['resources']

    def match(self, cfn):
        return alphanumeric_name(cfn, 'Resources')
