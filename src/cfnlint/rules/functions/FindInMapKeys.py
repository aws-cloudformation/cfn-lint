"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class FindInMapKeys(CloudFormationLintRule):
    """Check if FindInMap values are correct"""
    id = 'W1011'
    shortdesc = 'FindInMap keys exist in the map'
    description = 'Checks the keys in a FindInMap to make sure they exist. ' \
                  'Check only if the Map Name is a string and if the key is a string.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-findinmap.html'
    tags = ['functions', 'findinmap']

    def check_keys(self, map_name, keys, mappings, tree):
        """ Check the validity of the first key """
        matches = []
        first_key = keys[0]
        second_key = keys[1]
        if isinstance(second_key, (six.string_types, int)):
            if isinstance(map_name, (six.string_types)):
                mapping = mappings.get(map_name)
                if mapping:
                    if isinstance(first_key, (six.string_types, int)):
                        if isinstance(map_name, (six.string_types)):
                            if mapping.get(first_key) is None:
                                message = 'FindInMap first key "{0}" doesn\'t exist in map "{1}" at {3}'
                                matches.append(RuleMatch(
                                    tree[:] + [1],
                                    message.format(first_key, map_name, first_key, '/'.join(map(str, tree)))))
                        if mapping.get(first_key):
                            # Don't double error if they first key doesn't exist
                            if mapping.get(first_key, {}).get(second_key) is None:
                                message = 'FindInMap second key "{0}" doesn\'t exist in map "{1}" under "{2}" at {3}'
                                matches.append(RuleMatch(
                                    tree[:] + [2],
                                    message.format(second_key, map_name, first_key, '/'.join(map(str, tree)))))
                    else:
                        for key, value in mapping.items():
                            if value.get(second_key) is None:
                                message = 'FindInMap second key "{0}" doesn\'t exist in map "{1}" under "{2}" at {3}'
                                matches.append(RuleMatch(
                                    tree[:] + [2],
                                    message.format(second_key, map_name, key, '/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        matches = []

        findinmaps = cfn.search_deep_keys('Fn::FindInMap')
        mappings = cfn.get_mappings()
        for findinmap in findinmaps:
            tree = findinmap[:-1]
            map_obj = findinmap[-1]

            if len(map_obj) == 3:
                matches.extend(self.check_keys(map_obj[0], map_obj[1:], mappings, tree))

        return matches
