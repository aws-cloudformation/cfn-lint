"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitName(CloudFormationLintRule):
    """Check if maximum Parameter name size limit is exceeded"""
    id = 'E2011'
    shortdesc = 'Parameter name limit not exceeded'
    description = 'Check the size of Parameter names in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        """Check CloudFormation Parameters"""
        matches = []
        for parameter_name in cfn.template.get('Parameters', {}):
            if len(parameter_name) > LIMITS['Parameters']['name']:
                message = 'The length of parameter name ({0}) exceeds the limit ({1})'
                matches.append(RuleMatch(['Parameters', parameter_name], message.format(len(parameter_name), LIMITS['Parameters']['name'])))
        return matches
