"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitDescription(CloudFormationLintRule):
    """Check maximum Output description size limit"""
    id = 'I6012'
    shortdesc = 'Output description limit'
    description = 'Check the size of Output description in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        outputs = cfn.template.get('Outputs', {})

        for output_name, output_value in outputs.items():
            description = output_value.get('Description')
            if description:
                path = ['Outputs', output_name, 'Description']
                if LIMITS['threshold'] * LIMITS['outputs']['description'] < len(description) <= LIMITS['outputs']['description']:
                    message = 'The length of output description ({0}) is approaching the limit ({1})'
                    matches.append(RuleMatch(path, message.format(
                        len(description), LIMITS['outputs']['description'])))

        return matches
