"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitNumber(CloudFormationLintRule):
    """Check if maximum Mapping limit is exceeded"""
    id = 'E7010'
    shortdesc = 'Mapping limit not exceeded'
    description = 'Check the number of Mappings in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['mappings', 'limits']

    def match(self, cfn):
        """Check CloudFormation Mappings"""

        matches = []

        # Check number of mappings against the defined limit
        mappings = cfn.template.get('Mappings', {})
        if len(mappings) > LIMITS['mappings']['number']:
            message = 'The number of mappings ({0}) exceeds the limit ({1})'
            matches.append(RuleMatch(['Mappings'], message.format(
                len(mappings), LIMITS['mappings']['number'])))

        return matches
