"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.common import name_limit


class LimitName(CloudFormationLintRule):
    """Check if maximum Parameter name size limit is exceeded"""
    id = 'E2011'
    shortdesc = 'Parameter name limit not exceeded'
    description = 'Check the size of Parameter names in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        return name_limit(cfn, 'Parameters')
