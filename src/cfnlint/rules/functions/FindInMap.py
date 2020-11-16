"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class FindInMap(CloudFormationLintRule):
    """Check if FindInMap values are correct"""
    id = 'E1011'
    shortdesc = 'FindInMap validation of configuration'
    description = 'Making sure the function is a list of appropriate config'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-findinmap.html'
    tags = ['functions', 'findinmap']

    supported_functions = [
        'Fn::FindInMap',
        'Ref'
    ]

    def check_dict(self, obj, tree):
        """
            Check that obj is a dict with Ref as the only key
            Mappings only support Ref inside them
        """
        matches = []

        if isinstance(obj, dict):
            if len(obj) == 1:
                for key_name, _ in obj.items():
                    if key_name not in self.supported_functions:
                        message = 'FindInMap only supports [{0}] functions at {1}'
                        matches.append(RuleMatch(
                            tree[:] + [key_name],
                            message.format(
                                ', '.join(map(str, self.supported_functions)),
                                '/'.join(map(str, tree)))))
            else:
                message = 'FindInMap only supports an object of 1 of [{0}] functions at {1}'
                matches.append(RuleMatch(
                    tree[:],
                    message.format(
                        ', '.join(map(str, self.supported_functions)),
                        '/'.join(map(str, tree)))))

        return matches

    def map_name(self, map_name, mappings, tree):
        """ Check the map name """
        matches = []
        if isinstance(map_name, (six.string_types, dict)):
            if isinstance(map_name, dict):
                matches.extend(self.check_dict(map_name, tree[:] + [0]))
            else:
                if map_name not in mappings:
                    message = 'Map Name {0} does not exist for {0}'
                    matches.append(RuleMatch(
                        tree[:] + [0], message.format(map_name, '/'.join(map(str, tree)))))
        else:
            message = 'Map Name should be a {0}, or string at {1}'
            matches.append(RuleMatch(
                tree[:] + [0],
                message.format(
                    ', '.join(map(str, self.supported_functions)),
                    '/'.join(map(str, tree)))))

        return matches

    def first_key(self, first_key, tree):
        """ Check the validity of the first key """
        matches = []
        if isinstance(first_key, (six.string_types, int)):
            return matches
        if isinstance(first_key, (dict)):
            matches.extend(self.check_dict(first_key, tree[:] + [1]))
        else:
            message = 'FindInMap first key should be a {0}, string, or int at {1}'
            matches.append(RuleMatch(
                tree[:] + [1],
                message.format(
                    ', '.join(map(str, self.supported_functions)),
                    '/'.join(map(str, tree)))))

        return matches

    def second_key(self, second_key, tree):
        """ Check the validity of the second key """
        matches = []
        if isinstance(second_key, (six.string_types, int)):
            return matches

        if isinstance(second_key, (dict)):
            matches.extend(self.check_dict(second_key, tree[:] + [2]))
        else:
            message = 'FindInMap second key should be a {0}, string, or int at {1}'
            matches.append(RuleMatch(
                tree[:] + [2],
                message.format(
                    ', '.join(map(str, self.supported_functions)),
                    '/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        matches = []

        findinmaps = cfn.search_deep_keys('Fn::FindInMap')
        mappings = cfn.get_mappings()
        for findinmap in findinmaps:
            tree = findinmap[:-1]
            map_obj = findinmap[-1]
            if not isinstance(map_obj, list):
                message = 'FindInMap is a list with 3 values for {0}'
                matches.append(RuleMatch(
                    tree[:], message.format('/'.join(tree))))
                continue
            if len(map_obj) == 3:
                map_name = map_obj[0]
                first_key = map_obj[1]
                second_key = map_obj[2]

                matches.extend(self.map_name(map_name, mappings, tree))
                matches.extend(self.first_key(first_key, tree))
                matches.extend(self.second_key(second_key, tree))

            else:
                message = 'FindInMap is a list with 3 values for {0}'
                matches.append(RuleMatch(
                    tree[:] + [1], message.format('/'.join(map(str, tree)))))

        return matches
