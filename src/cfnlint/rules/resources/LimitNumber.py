"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitNumber(CloudFormationLintRule):
    """Check if maximum Resource limit is exceeded"""
    id = 'E3010'
    shortdesc = 'Resource limit not exceeded'
    description = 'Check the number of Resources in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['resources', 'limits']

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        # Check number of resources against the defined limit
        resources = cfn.get_resources()
        if len(resources) > LIMITS['resources']['number']:
            message = 'The number of resources ({0}) exceeds the limit ({1})'
            matches.append(RuleMatch(['Resources'], message.format(len(resources), LIMITS['resources']['number'])))

        return matches
