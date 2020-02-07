"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitName(CloudFormationLintRule):
    """Check maximum Parameter name size limit"""
    id = 'I2011'
    shortdesc = 'Parameter name limit'
    description = 'Check the size of Parameter names in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        parameters = cfn.template.get('Parameters', {})

        for parameter_name in parameters:
            path = ['Parameters', parameter_name]
            if LIMITS['threshold'] * LIMITS['parameters']['name'] < len(parameter_name) <= LIMITS['parameters']['name']:
                message = 'The length of parameter name ({0}) is approaching the limit ({1})'
                matches.append(RuleMatch(path, message.format(
                    len(parameter_name), LIMITS['parameters']['name'])))

        return matches
