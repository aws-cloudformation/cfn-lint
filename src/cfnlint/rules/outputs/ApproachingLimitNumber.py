"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import approaching_number_limit


class LimitNumber(CloudFormationLintRule):
    """Check maximum Output limit"""
    id = 'I6010'
    shortdesc = 'Output limit'
    description = 'Check the number of Outputs in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        return approaching_number_limit(cfn, 'Outputs')
