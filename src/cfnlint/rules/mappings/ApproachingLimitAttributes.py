"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitAttributes(CloudFormationLintRule):
    """Check maximum Mapping attribute limit"""
    id = 'I7012'
    shortdesc = 'Mapping attribute limit'
    description = 'Check if the amount of Mapping attributes in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['mappings', 'limits']

    def match(self, cfn):
        """Check CloudFormation Mappings"""

        matches = []

        mappings = cfn.template.get('Mappings', {})

        for mapping_name, mapping in mappings.items():

            for mapping_attribute_name, mapping_attribute in mapping.items():
                path = ['Mappings', mapping_name, mapping_attribute_name]
                if LIMITS['threshold'] * LIMITS['mappings']['attributes'] < len(mapping_attribute) <= LIMITS['mappings']['attributes']:
                    message = 'The amount of mapping attributes ({0}) is approaching the limit ({1})'
                    matches.append(RuleMatch(path, message.format(
                        len(mapping_attribute), LIMITS['mappings']['attributes'])))

        return matches
