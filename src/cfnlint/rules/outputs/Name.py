"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import alphanumeric_name


class Name(CloudFormationLintRule):
    """Check if Outputs are named correctly"""
    id = 'E6004'
    shortdesc = 'Outputs have appropriate names'
    description = 'Check if Outputs are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs']

    def match(self, cfn):
        return alphanumeric_name(cfn, 'Outputs')
