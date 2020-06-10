"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import RuleMatch


def check_condition_list(cfn, function):
    matches = []
    # Build the list of functions
    trees = cfn.search_deep_keys(function)
    for tree in trees:
        # Test when in Conditions
        if tree[0] == 'Conditions':
            value = tree[-1]
            if not isinstance(value, list):
                message = function + ' must be a condition list'
                matches.append(RuleMatch(
                    tree[:-1],
                    message.format()
                ))
            elif function == 'Fn::Not' and not len(value) == 1:
                message = function + ' must be a list of exactly 1 condition'
                matches.append(RuleMatch(
                    tree[:-1],
                    message.format()
                ))
            elif function != 'Fn::Not' and not (2 <= len(value) <= 10):
                message = function + ' must be a list of between 2 to 10 conditions'
                matches.append(RuleMatch(
                    tree[:-1],
                    message.format()
                ))
            else:
                for index, element in enumerate(value):
                    if isinstance(element, dict):
                        if len(element) == 1:
                            for element_key in element.keys():
                                if element_key not in ['Fn::And', 'Fn::Or', 'Fn::Not', 'Condition', 'Fn::Equals']:
                                    message = function + ' list must be another valid condition'
                                    matches.append(RuleMatch(
                                        tree[:-1] + [index, element_key],
                                        message.format()
                                    ))
                        else:
                            message = function + ' list must be another valid condition'
                            matches.append(RuleMatch(
                                tree[:-1] + [index],
                                message.format()
                            ))
                    else:
                        message = function + ' list must be another valid condition'
                        matches.append(RuleMatch(
                            tree[:-1] + [index],
                            message.format()
                        ))
    return matches
