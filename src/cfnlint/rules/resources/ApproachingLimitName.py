"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.limits import approaching_name_limit


class LimitName(CloudFormationLintRule):
    """Check maximum Resource name size limit"""
    id = 'I3011'
    shortdesc = 'Resource name limit'
    description = 'Check the size of Resource names in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['resources', 'limits']

    def match(self, cfn):
        """Check CloudFormation Resources"""
        return approaching_name_limit(cfn, 'Resources')
