"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import approaching_name_limit


class LimitName(CloudFormationLintRule):
    """Check maximum Parameter name size limit"""
    id = 'I2011'
    shortdesc = 'Parameter name limit'
    description = 'Check the size of Parameter names in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        return approaching_name_limit(cfn, 'Parameters')
