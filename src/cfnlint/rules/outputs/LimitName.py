"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitName(CloudFormationLintRule):
    """Check if maximum Output name size limit is exceeded"""
    id = 'E6011'
    shortdesc = 'Output name limit not exceeded'
    description = 'Check the size of Output names in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        outputs = cfn.template.get('Outputs', {})

        for output_name in outputs:
            path = ['Outputs', output_name]
            if len(output_name) > LIMITS['outputs']['name']:
                message = 'The length of output name ({0}) exceeds the limit ({1})'
                matches.append(RuleMatch(path, message.format(
                    len(output_name), LIMITS['outputs']['name'])))

        return matches
