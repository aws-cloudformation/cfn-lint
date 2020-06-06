"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Equals(CloudFormationLintRule):
    """Check Equals Condition Function Logic"""
    id = 'E8003'
    shortdesc = 'Check Fn::Equals structure for validity'
    description = 'Check Fn::Equals is a list of two elements'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-equals'
    tags = ['functions', 'equals']

    def match(self, cfn):
        function = 'Fn::Equals'
        matches = []
        # Build the list of functions
        trees = cfn.search_deep_keys(function)

        allowed_functions = ['Ref', 'Fn::FindInMap',
                             'Fn::Sub', 'Fn::Join', 'Fn::Select', 'Fn::Split']

        for tree in trees:
            # Test when in Conditions
            if tree[0] == 'Conditions':
                value = tree[-1]
                if not isinstance(value, list):
                    message = function + ' must be a list of two elements'
                    matches.append(RuleMatch(
                        tree[:-1],
                        message.format()
                    ))
                elif len(value) != 2:
                    message = function + ' must be a list of two elements'
                    matches.append(RuleMatch(
                        tree[:-1],
                        message.format()
                    ))
                else:
                    for index, element in enumerate(value):
                        if isinstance(element, dict):
                            if len(element) == 1:
                                for element_key in element.keys():
                                    if element_key not in allowed_functions:
                                        message = function + ' element must be a supported function ({0})'
                                        matches.append(RuleMatch(
                                            tree[:-1] + [index, element_key],
                                            message.format(', '.join(allowed_functions))
                                        ))
                            else:
                                message = function + ' element must be a supported function ({0})'
                                matches.append(RuleMatch(
                                    tree[:-1] + [index],
                                    message.format(', '.join(allowed_functions))
                                ))
                        elif not isinstance(element, (six.string_types, bool, six.integer_types, float)):
                            message = function + ' element must be a String, Boolean, Number, or supported function ({0})'
                            matches.append(RuleMatch(
                                tree[:-1] + [index],
                                message.format(', '.join(allowed_functions))
                            ))

        return matches
