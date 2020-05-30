"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitName(CloudFormationLintRule):
    """Check if maximum Resource name size limit is exceeded"""
    id = 'E3011'
    shortdesc = 'Resource name limit not exceeded'
    description = 'Check the size of Resource names in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['resources', 'limits']

    def match(self, cfn):
        """Check CloudFormation Resources"""
        matches = []
        for resource_name in cfn.template.get('Resources', {}):
            if len(resource_name) > LIMITS['resources']['name']:
                message = 'The length of resource name ({0}) exceeds the limit ({1})'
                matches.append(RuleMatch(['Resources', resource_name], message.format(len(resource_name), LIMITS['resources']['name'])))
        return matches
