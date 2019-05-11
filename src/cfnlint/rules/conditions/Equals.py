"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


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

        allowed_functions = ['Ref', 'Fn::FindInMap', 'Fn::Sub', 'Fn::Join', 'Fn::Select', 'Fn::Split']

        for equal_tree in equal_trees:
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
