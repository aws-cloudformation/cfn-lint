"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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


class Select(CloudFormationLintRule):
    """Check if Select values are correct"""
    id = 'E1017'
    shortdesc = 'Select validation of parameters'
    description = 'Making sure the function not is of list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html'
    tags = ['functions', 'select']

    def match(self, cfn):
        """Check CloudFormation Select"""

        matches = []

        select_objs = cfn.search_deep_keys('Fn::Select')

        supported_functions = [
            'Fn::FindInMap',
            'Fn::GetAtt',
            'Fn::GetAZs',
            'Fn::If',
            'Fn::Split',
            'Fn::Cidr',
            'Ref'
        ]

        for select_obj in select_objs:
            select_value_obj = select_obj[-1]
            tree = select_obj[:-1]
            if isinstance(select_value_obj, list):
                if len(select_value_obj) == 2:
                    index_obj = select_value_obj[0]
                    list_of_objs = select_value_obj[1]
                    if isinstance(index_obj, dict):
                        if len(index_obj) == 1:
                            for index_key, _ in index_obj.items():
                                if index_key not in ['Ref', 'Fn::FindInMap']:
                                    message = 'Select index should be an Integer or a function Ref or FindInMap for {0}'
                                    matches.append(RuleMatch(
                                        tree, message.format('/'.join(map(str, tree)))))
                    elif not isinstance(index_obj, six.integer_types):
                        try:
                            int(index_obj)
                        except ValueError:
                            message = 'Select index should be an Integer or a function of Ref or FindInMap for {0}'
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree)))))
                    if isinstance(list_of_objs, dict):
                        if len(list_of_objs) == 1:
                            for key, _ in list_of_objs.items():
                                if key not in supported_functions:
                                    message = 'Select should use a supported function of {0}'
                                    matches.append(RuleMatch(
                                        tree, message.format(', '.join(map(str, supported_functions)))))
                        else:
                            message = 'Select should use a supported function of {0}'
                            matches.append(RuleMatch(
                                tree, message.format(', '.join(map(str, supported_functions)))))
                    elif not isinstance(list_of_objs, list):
                        message = 'Select should be an array of values for {0}'
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Select should be a list of 2 elements for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = 'Select should be a list of 2 elements for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
