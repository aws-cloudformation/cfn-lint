"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Not(CloudFormationLintRule):
    """Check Not Condition Function Logic"""
    id = 'E8005'
    shortdesc = 'Check Fn::Not structure for validity'
    description = 'Check Fn::Not is a list of two elements'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-not'
    tags = ['functions', 'not']

    def match(self, cfn):
        """Check CloudFormation Not"""

        matches = []

        # Build the list of functions
        not_trees = cfn.search_deep_keys('Fn::Not')

        for not_tree in not_trees:
            # Test when in Conditions
            if not_tree[0] == 'Conditions':
                not_value = not_tree[-1]
                if not isinstance(not_value, list):
                    message = 'Fn::Not must be a list of exactly 1 condition'
                    matches.append(RuleMatch(
                        not_tree[:-1],
                        message.format()
                    ))
                elif not len(not_value) == 1:
                    message = 'Fn::Not must be a list of exactly 1 condition'
                    matches.append(RuleMatch(
                        not_tree[:-1],
                        message.format()
                    ))
                else:
                    for index, element in enumerate(not_value):
                        if isinstance(element, dict):
                            if len(element) == 1:
                                for element_key in element.keys():
                                    if element_key not in ['Fn::And', 'Fn::Or', 'Fn::Not', 'Condition', 'Fn::Equals']:
                                        message = 'Fn::Not list must be another valid condition'
                                        matches.append(RuleMatch(
                                            not_tree[:-1] + [index, element_key],
                                            message.format()
                                        ))
                            else:
                                message = 'Fn::Not list must be another valid condition'
                                matches.append(RuleMatch(
                                    not_tree[:-1] + [index],
                                    message.format()
                                ))
                        else:
                            message = 'Fn::Not list must be another valid condition'
                            matches.append(RuleMatch(
                                not_tree[:-1] + [index],
                                message.format()
                            ))

        return matches
