"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Or(CloudFormationLintRule):
    """Check Or Condition Function Logic"""
    id = 'E8006'
    shortdesc = 'Check Fn::Or structure for validity'
    description = 'Check Fn::Or is a list of two elements'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-or'
    tags = ['functions', 'or']

    def match(self, cfn):
        """Check CloudFormation Or"""

        matches = []

        # Build the list of functions
        or_trees = cfn.search_deep_keys('Fn::Or')

        for or_tree in or_trees:
            # Test when in Conditions
            if or_tree[0] == 'Conditions':
                or_value = or_tree[-1]
                if not isinstance(or_value, list):
                    message = 'Fn::Or must be a list of between 2 to 10 conditions'
                    matches.append(RuleMatch(
                        or_tree[:-1],
                        message.format()
                    ))
                elif not (2 <= len(or_value) <= 10):
                    message = 'Fn::Or must be a list of between 2 to 10 conditions'
                    matches.append(RuleMatch(
                        or_tree[:-1],
                        message.format()
                    ))
                else:
                    for index, element in enumerate(or_value):
                        if isinstance(element, dict):
                            if len(element) == 1:
                                for element_key in element.keys():
                                    if element_key not in ['Fn::And', 'Fn::Or', 'Fn::Not', 'Condition', 'Fn::Equals']:
                                        message = 'Fn::Or list must be another valid condition'
                                        matches.append(RuleMatch(
                                            or_tree[:-1] + [index, element_key],
                                            message.format()
                                        ))
                            else:
                                message = 'Fn::Or list must be another valid condition'
                                matches.append(RuleMatch(
                                    or_tree[:-1] + [index],
                                    message.format()
                                ))
                        else:
                            message = 'Fn::Or list must be another valid condition'
                            matches.append(RuleMatch(
                                or_tree[:-1] + [index],
                                message.format()
                            ))

        return matches
