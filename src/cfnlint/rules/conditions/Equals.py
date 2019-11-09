"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
        """Check CloudFormation Equals"""

        matches = []

        # Build the list of functions
        equal_trees = cfn.search_deep_keys('Fn::Equals')

        allowed_functions = ['Ref', 'Fn::FindInMap',
                             'Fn::Sub', 'Fn::Join', 'Fn::Select', 'Fn::Split']

        for equal_tree in equal_trees:
            # Test when in Conditions
            if equal_tree[0] == 'Conditions':
                equal = equal_tree[-1]
                if not isinstance(equal, list):
                    message = 'Fn::Equals must be a list of two elements'
                    matches.append(RuleMatch(
                        equal_tree[:-1],
                        message.format()
                    ))
                elif len(equal) != 2:
                    message = 'Fn::Equals must be a list of two elements'
                    matches.append(RuleMatch(
                        equal_tree[:-1],
                        message.format()
                    ))
                else:
                    for index, element in enumerate(equal):
                        if isinstance(element, dict):
                            if len(element) == 1:
                                for element_key in element.keys():
                                    if element_key not in allowed_functions:
                                        message = 'Fn::Equals element must be a supported function ({0})'
                                        matches.append(RuleMatch(
                                            equal_tree[:-1] + [index, element_key],
                                            message.format(', '.join(allowed_functions))
                                        ))
                            else:
                                message = 'Fn::Equals element must be a supported function ({0})'
                                matches.append(RuleMatch(
                                    equal_tree[:-1] + [index],
                                    message.format(', '.join(allowed_functions))
                                ))
                        elif not isinstance(element, (six.string_types, bool, six.integer_types, float)):
                            message = 'Fn::Equals element must be a String, Boolean, Number, or supported function ({0})'
                            matches.append(RuleMatch(
                                equal_tree[:-1] + [index],
                                message.format(', '.join(allowed_functions))
                            ))

        return matches
