"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import approaching_number_limit


class LimitNumber(CloudFormationLintRule):
    """Check maximum Mapping limit"""
    id = 'I7010'
    shortdesc = 'Mapping limit'
    description = 'Check the number of Mappings in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['mappings', 'limits']

    def match(self, cfn):
        return approaching_number_limit(cfn, 'Mappings')
