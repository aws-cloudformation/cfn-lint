"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitName(CloudFormationLintRule):
    """Check if maximum Mapping name size limit is exceeded"""
    id = 'E7011'
    shortdesc = 'Mapping name limit not exceeded'
    description = 'Check the size of Mapping names in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['mappings', 'limits']

    def match(self, cfn):
        """Check CloudFormation Mappings"""

        matches = []

        mappings = cfn.template.get('Mappings', {})

        for mapping_name in mappings:
            path = ['Mappings', mapping_name]
            if len(mapping_name) > LIMITS['mappings']['name']:
                message = 'The length of mapping name ({0}) exceeds the limit ({1})'
                matches.append(RuleMatch(path, message.format(
                    len(mapping_name), LIMITS['mappings']['name'])))

        return matches
