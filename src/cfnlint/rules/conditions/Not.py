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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


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
                                    message = 'Fn::Or list must be another valid condition'
                                    matches.append(RuleMatch(
                                        not_tree[:-1] + [index, element_key],
                                        message.format()
                                    ))
                        else:
                            message = 'Fn::Or list must be another valid condition'
                            matches.append(RuleMatch(
                                not_tree[:-1] + [index],
                                message.format()
                            ))
                    else:
                        message = 'Fn::Or list must be another valid condition'
                        matches.append(RuleMatch(
                            not_tree[:-1] + [index],
                            message.format()
                        ))

        return matches
