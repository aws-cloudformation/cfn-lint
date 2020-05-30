"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitName(CloudFormationLintRule):
    """Check maximum Output name size limit"""
    id = 'I6011'
    shortdesc = 'Output name limit'
    description = 'Check the size of Output names in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        """Check CloudFormation Outputs"""
        matches = []
        for output_name in cfn.template.get('Outputs', {}):
            if LIMITS['threshold'] * LIMITS['Outputs']['name'] < len(output_name) <= LIMITS['Outputs']['name']:
                message = 'The length of output name ({0}) is approaching the limit ({1})'
                matches.append(RuleMatch(['Outputs', output_name], message.format(len(output_name), LIMITS['Outputs']['name'])))
        return matches
