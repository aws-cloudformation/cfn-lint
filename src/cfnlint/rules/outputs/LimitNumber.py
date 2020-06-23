"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import number_limit


class LimitNumber(CloudFormationLintRule):
    """Check if maximum Output limit is exceeded"""
    id = 'E6010'
    shortdesc = 'Output limit not exceeded'
    description = 'Check the number of Outputs in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        return number_limit(cfn, 'Outputs')
