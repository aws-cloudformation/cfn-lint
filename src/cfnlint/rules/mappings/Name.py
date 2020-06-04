"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import alphanumeric_name


class Name(CloudFormationLintRule):
    """Check if Mappings are named correctly"""
    id = 'E7002'
    shortdesc = 'Mappings have appropriate names'
    description = 'Check if Mappings are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html'
    tags = ['mappings']

    def match(self, cfn):
        return alphanumeric_name(cfn, 'Mappings')
