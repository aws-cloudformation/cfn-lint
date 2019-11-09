"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class And(CloudFormationLintRule):
    """Check And Condition Function Logic"""
    id = 'E8004'
    shortdesc = 'Check Fn::And structure for validity'
    description = 'Check Fn::And is a list of two elements'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-and'
    tags = ['functions', 'and']

    def match(self, cfn):
        """Check CloudFormation And"""

        matches = []

        # Build the list of functions
        equal_trees = cfn.search_deep_keys('Fn::And')

        for equal_tree in equal_trees:
            # Test when in Conditions
            if equal_tree[0] == 'Conditions':
                equal = equal_tree[-1]
                if not isinstance(equal, list):
                    message = 'Fn::And must be a list of between 2 to 10 conditions'
                    matches.append(RuleMatch(
                        equal_tree[:-1],
                        message.format()
                    ))
                elif not (2 <= len(equal) <= 10):
                    message = 'Fn::And must be a list of between 2 to 10 conditions'
                    matches.append(RuleMatch(
                        equal_tree[:-1],
                        message.format()
                    ))
                else:
                    for index, element in enumerate(equal):
                        if isinstance(element, dict):
                            if len(element) == 1:
                                for element_key in element.keys():
                                    if element_key not in ['Fn::And', 'Fn::Or', 'Fn::Not', 'Condition', 'Fn::Equals']:
                                        message = 'Fn::And list must be another valid condition'
                                        matches.append(RuleMatch(
                                            equal_tree[:-1] + [index, element_key],
                                            message.format()
                                        ))
                            else:
                                message = 'Fn::And list must be another valid condition'
                                matches.append(RuleMatch(
                                    equal_tree[:-1] + [index],
                                    message.format()
                                ))
                        else:
                            message = 'Fn::And list must be another valid condition'
                            matches.append(RuleMatch(
                                equal_tree[:-1] + [index],
                                message.format()
                            ))

        return matches
