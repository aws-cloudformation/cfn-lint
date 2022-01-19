"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import REGEX_ALPHANUMERIC


class KeyName(CloudFormationLintRule):
    """Check if Mapping Keys are type string"""
    id = 'E7003'
    shortdesc = 'Mapping keys are strings and alphanumeric'
    description = 'Check if Mappings keys are properly typed as strings and alphanumeric'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html'
    tags = ['mappings']

    def check_attribute(self, key, path):
        """ Check the key name for string and alphanumeric"""
        matches = []
        if not isinstance(key, str):
            message = 'Mapping attribute ({0}) has to be a string.'
            matches.append(RuleMatch(path[:], message.format(key)))
        elif not re.match(REGEX_ALPHANUMERIC, key):
            message = 'Mapping attribute ({0}) has invalid name. Name has to be alphanumeric.'
            matches.append(RuleMatch(path[:], message.format(key)))

        return matches

    def check_key(self, key, path):
        """ Check the key name for string and alphanumeric"""
        matches = []
        if not isinstance(key, str):
            message = 'Mapping key ({0}) has to be a string.'
            matches.append(RuleMatch(path[:], message.format(key)))
        elif not re.match('^[a-zA-Z0-9.-]{1,255}$', key) and key != 'Fn::Transform':
            message = 'Mapping key ({0}) has invalid name. Name has to be alphanumeric, \'-\' or \'.\''
            matches.append(RuleMatch(path[:], message.format(key)))

        return matches

    def match(self, cfn):
        matches = []

        mappings = cfn.template.get('Mappings', {})
        for mapping_name, mapping_value in mappings.items():
            if isinstance(mapping_value, dict):
                for key_name, key_value in mapping_value.items():
                    matches.extend(self.check_key(
                        key_name, ['Mappings', mapping_name, key_name]))
                    if isinstance(key_value, dict):
                        for sub_key_name, _ in key_value.items():
                            matches.extend(
                                self.check_attribute(
                                    sub_key_name, ['Mappings', mapping_name, key_name, sub_key_name]))

        return matches
