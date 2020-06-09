"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitAttributes(CloudFormationLintRule):
    """Check if maximum Mapping attribute limit is exceeded"""
    id = 'E7012'
    shortdesc = 'Mapping attribute limit not exceeded'
    description = 'Check if the amount of Mapping attributes in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['mappings', 'limits']

    def match(self, cfn):
        matches = []
        for mapping_name, mapping in cfn.template.get('Mappings', {}).items():
            for mapping_attribute_name, mapping_attribute in mapping.items():
                path = ['Mappings', mapping_name, mapping_attribute_name]
                if len(mapping_attribute) > LIMITS['Mappings']['attributes']:
                    message = 'The amount of mapping attributes ({0}) exceeds the limit ({1})'
                    matches.append(RuleMatch(path, message.format(len(mapping_attribute), LIMITS['Mappings']['attributes'])))
        return matches
