"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.helpers import VALID_PARAMETER_TYPES_LIST
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Equals(CloudFormationLintRule):
    """Check Equals Condition Function Logic"""
    id = 'E8003'
    shortdesc = 'Check Fn::Equals structure for validity'
    description = 'Check Fn::Equals is a list of two elements'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-equals'
    tags = ['functions', 'equals']

    allowed_functions = ['Ref', 'Fn::FindInMap',
                         'Fn::Sub', 'Fn::Join', 'Fn::Select', 'Fn::Split']
    function = 'Fn::Equals'

    def _check_equal_values(self, element, path, valid_refs):
        matches = []

        if len(element) == 1:
            for element_key, element_value in element.items():
                if element_key not in self.allowed_functions:
                    message = self.function + \
                        ' element must be a supported function ({0})'
                    matches.append(RuleMatch(
                        path[:] + [element_key],
                        message.format(', '.join(self.allowed_functions))
                    ))
                elif element_key == 'Ref':
                    valid_ref = valid_refs.get(element_value)
                    if valid_ref:
                        if valid_ref.get('From') == 'Parameters':
                            if valid_ref.get('Type') in VALID_PARAMETER_TYPES_LIST:
                                message = 'Every Fn::Equals object requires a list of 2 string parameters'
                                matches.append(RuleMatch(
                                    path, message))
        else:
            message = self.function + ' element must be a supported function ({0})'
            matches.append(RuleMatch(
                path,
                message.format(', '.join(self.allowed_functions))
            ))
        return matches

    def match(self, cfn):
        matches = []
        # Build the list of functions
        trees = cfn.search_deep_keys(self.function)

        valid_refs = cfn.get_valid_refs()
        for tree in trees:
            # Test when in Conditions
            if tree[0] == 'Conditions':
                value = tree[-1]
                if not isinstance(value, list):
                    message = self.function + ' must be a list of two elements'
                    matches.append(RuleMatch(
                        tree[:-1],
                        message.format()
                    ))
                elif len(value) != 2:
                    message = self.function + ' must be a list of two elements'
                    matches.append(RuleMatch(
                        tree[:-1],
                        message.format()
                    ))
                else:
                    for index, element in enumerate(value):
                        if isinstance(element, dict):
                            matches.extend(self._check_equal_values(
                                element, tree[:-1] + [index], valid_refs))
                        elif not isinstance(element, (six.string_types, bool, six.integer_types, float)):
                            message = self.function + \
                                ' element must be a String, Boolean, Number, or supported function ({0})'
                            matches.append(RuleMatch(
                                tree[:-1] + [index],
                                message.format(', '.join(self.allowed_functions))
                            ))

        return matches
