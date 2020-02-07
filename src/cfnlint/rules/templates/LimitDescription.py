"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitDescription(CloudFormationLintRule):
    """Check Template Description Size"""
    id = 'E1003'
    shortdesc = 'Template description limit'
    description = 'Check if the size of the template description is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['limits']

    def match(self, cfn):
        """Basic Matching"""
        matches = []

        description = cfn.template.get('Description', '')

        if len(description) > LIMITS['template']['description']:
            path = ['Template', 'Description']
            message = 'The template description ({0} bytes) exceeds the limit ({1} bytes)'
            matches.append(RuleMatch(path, message.format(len(description), LIMITS['template']['description'])))

        return matches
