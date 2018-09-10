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


class Join(CloudFormationLintRule):
    """Check if Join values are correct"""
    id = 'E1022'
    shortdesc = 'Join validation of parameters'
    description = 'Making sure the join function is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-join.html'
    tags = ['functions', 'join']

    def match(self, cfn):
        """Check CloudFormation Join"""

        matches = []

        join_objs = cfn.search_deep_keys('Fn::Join')

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::GetAtt',
            'Fn::GetAZs',
            'Fn::ImportValue',
            'Fn::If',
            'Fn::Join',
            'Fn::Select',
            'Fn::Split',
            'Fn::Sub',
            'Ref'
        ]

        for join_obj in join_objs:
            join_value_obj = join_obj[-1]
            tree = join_obj[:-1]
            if isinstance(join_value_obj, list):
                if len(join_value_obj) == 2:
                    join_string = join_value_obj[0]
                    join_string_objs = join_value_obj[1]
                    if not isinstance(join_string, six.string_types):
                        message = 'Join string has to be of type string for {0}'
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                    if isinstance(join_string_objs, dict):
                        if isinstance(join_string_objs, dict):
                            if len(join_string_objs) == 1:
                                for key, _ in join_string_objs.items():
                                    if key not in supported_functions:
                                        message = 'Join unsupported function for {0}'
                                        matches.append(RuleMatch(
                                            tree, message.format('/'.join(map(str, tree)))))
                            else:
                                message = 'Join list of values should be singular for {0}'
                                matches.append(RuleMatch(
                                    tree, message.format('/'.join(map(str, tree)))))
                        elif not isinstance(join_string_objs, six.string_types):
                            message = 'Join list of singular function or string for {0}'
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree)))))
                    elif not isinstance(join_string_objs, list):
                        message = 'Join list of values for {0}'
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                    else:
                        for string_obj in join_string_objs:
                            if isinstance(string_obj, dict):
                                if len(string_obj) == 1:
                                    for key, _ in string_obj.items():
                                        if key not in supported_functions:
                                            message = 'Join unsupported function for {0}'
                                            matches.append(RuleMatch(
                                                tree, message.format('/'.join(map(str, tree)))))
                                else:
                                    message = 'Join list of values should be singular for {0}'
                                    matches.append(RuleMatch(
                                        tree, message.format('/'.join(map(str, tree)))))
                            elif not isinstance(string_obj, six.string_types):
                                message = 'Join list of singular function or string for {0}'
                                matches.append(RuleMatch(
                                    tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Join should be an array of 2 for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = 'Join should be an array of 2 for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
