"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class PropertiesTagsRequired(CloudFormationLintRule):
    """Check if Tags have required keys"""
    id = 'E9000'
    shortdesc = 'Tags have correct key values'
    description = 'Check Tags for resources'
    tags = ['resources', 'tags']

    def match(self, cfn):
        """Check Tags for required keys"""

        matches = []

        required_tags = ['CostCenter', 'ApplicationName']

        all_tags = cfn.search_deep_keys('Tags')
        all_tags = [x for x in all_tags if x[0] == 'Resources']
        for all_tag in all_tags:
            all_keys = [d.get('Key') for d in all_tag[-1]]
            for required_tag in required_tags:
                if required_tag not in all_keys:
                    message = "Missing Tag {0} at {1}"
                    matches.append(
                        RuleMatch(
                            all_tag[:-1],
                            message.format(required_tag, '/'.join(map(str, all_tag[:-1])))))

        return matches
