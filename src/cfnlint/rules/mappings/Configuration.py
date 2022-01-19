"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Configuration(CloudFormationLintRule):
    """Check if Mappings are configured correctly"""
    id = 'E7001'
    shortdesc = 'Mappings are appropriately configured'
    description = 'Check if Mappings are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html'
    tags = ['mappings']

    def match(self, cfn):
        matches = []

        valid_map_types = (str, list, int, float)

        mappings = cfn.template.get('Mappings', {})
        if mappings:
            for mapname, mapobj in mappings.items():
                if not isinstance(mapobj, dict):
                    message = 'Mapping {0} has invalid property'
                    matches.append(RuleMatch(
                        ['Mappings', mapname],
                        message.format(mapname)
                    ))
                else:
                    for firstkey in mapobj:
                        firstkeyobj = mapobj[firstkey]
                        if not isinstance(firstkeyobj, dict):
                            message = 'Mapping {0} has invalid property at {1}'
                            matches.append(RuleMatch(
                                ['Mappings', mapname, firstkey],
                                message.format(mapname, firstkeyobj)
                            ))
                        else:
                            for secondkey in firstkeyobj:
                                if not isinstance(
                                        firstkeyobj[secondkey], valid_map_types):
                                    message = 'Mapping {0} has invalid property at {1}'
                                    matches.append(RuleMatch(
                                        ['Mappings', mapname, firstkey, secondkey],
                                        message.format(mapname, secondkey)
                                    ))

        return matches
