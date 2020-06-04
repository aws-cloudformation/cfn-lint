"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitNumber(CloudFormationLintRule):
    """Check maximum Resource limit"""
    id = 'I3010'
    shortdesc = 'Resource limit'
    description = 'Check the number of Resources in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['resources', 'limits']

    def match(self, cfn):
        matches = []
        resources = cfn.get_resources()
        if LIMITS['threshold'] * LIMITS['Resources']['number'] < len(resources) <= LIMITS['Resources']['number']:
            message = 'The number of resources ({0}) is approaching the limit ({1})'
            matches.append(RuleMatch(['Resources'], message.format(len(resources), LIMITS['Resources']['number'])))
        return matches
