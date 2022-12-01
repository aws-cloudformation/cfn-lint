"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class FindInMap(CloudFormationLintRule):
    """Check if FindInMap values are correct"""

    id = 'E1011'
    shortdesc = 'FindInMap validation of configuration'
    description = 'Making sure the function is a list of appropriate config'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-findinmap.html'
    tags = ['functions', 'findinmap']

    supported_functions = ['Fn::FindInMap', 'Ref']

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
                        matches.append(
                            RuleMatch(
                                tree[:] + [key_name],
                                message.format(
                                    ', '.join(map(str, self.supported_functions)),
                                    '/'.join(map(str, tree)),
                                ),
                            )
                        )
            else:
                message = (
                    'FindInMap only supports an object of 1 of [{0}] functions at {1}'
                )
                matches.append(
                    RuleMatch(
                        tree[:],
                        message.format(
                            ', '.join(map(str, self.supported_functions)),
                            '/'.join(map(str, tree)),
                        ),
                    )
                )

        return matches

    def map_name(self, map_name, mappings, tree):
        """Check the map name"""
        matches = []
        if isinstance(map_name, (str, dict)):
            if isinstance(map_name, dict):
                matches.extend(self.check_dict(map_name, tree[:] + [0]))
            else:
                if map_name not in mappings:
                    message = 'Map Name {0} does not exist for {0}'
                    matches.append(
                        RuleMatch(
                            tree[:] + [0],
                            message.format(map_name, '/'.join(map(str, tree))),
                        )
                    )
        else:
            message = 'Map Name should be a {0}, or string at {1}'
            matches.append(
                RuleMatch(
                    tree[:] + [0],
                    message.format(
                        ', '.join(map(str, self.supported_functions)),
                        '/'.join(map(str, tree)),
                    ),
                )
            )

        return matches

    def match_key(self, key, tree, key_name, key_index):
        """Check the validity of a key"""
        matches = []
        if isinstance(key, (str, int)):
            return matches
        if isinstance(key, dict):
            matches.extend(self.check_dict(key, tree[:] + [key_index]))
        else:
            message = 'FindInMap {0} should be a {1}, string, or int at {2}'
            matches.append(
                RuleMatch(
                    tree[:] + [key_index],
                    message.format(
                        key_name,
                        ', '.join(map(str, self.supported_functions)),
                        '/'.join(map(str, tree)),
                    ),
                )
            )

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
                matches.append(RuleMatch(tree[:], message.format('/'.join(tree))))
                continue
            if len(map_obj) == 3:
                map_name = map_obj[0]
                first_key = map_obj[1]
                second_key = map_obj[2]

                matches.extend(self.map_name(map_name, mappings, tree))
                matches.extend(self.match_key(first_key, tree, 'first key', 1))
                matches.extend(self.match_key(second_key, tree, 'second key', 2))

            else:
                message = 'FindInMap is a list with 3 values for {0}'
                matches.append(
                    RuleMatch(tree[:] + [1], message.format('/'.join(map(str, tree))))
                )

        return matches
