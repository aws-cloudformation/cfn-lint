"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitNumber(CloudFormationLintRule):
    """Check if maximum Parameter limit is exceeded"""
    id = 'E2010'
    shortdesc = 'Parameter limit not exceeded'
    description = 'Check the number of Parameters in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        # Check number of parameters against the defined limit
        parameters = cfn.template.get('Parameters', {})
        if len(parameters) > LIMITS['parameters']['number']:
            message = 'The number of parameters ({0}) exceeds the limit ({1})'
            matches.append(RuleMatch(['Parameters'], message.format(
                len(parameters), LIMITS['parameters']['number'])))

        return matches
