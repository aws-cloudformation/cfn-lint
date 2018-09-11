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


class Split(CloudFormationLintRule):
    """Check if Split values are correct"""
    id = 'E1018'
    shortdesc = 'Split validation of parameters'
    description = 'Making sure the split function is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-split.html'
    tags = ['functions', 'split']

    def match(self, cfn):
        """Check CloudFormation Join"""

        matches = []

        split_objs = cfn.search_deep_keys('Fn::Split')

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::GetAtt',
            'Fn::GetAZs',
            'Fn::ImportValue',
            'Fn::If',
            'Fn::Join',
            'Fn::Select',
            'Fn::Sub',
            'Ref'
        ]

        for split_obj in split_objs:
            split_value_obj = split_obj[-1]
            tree = split_obj[:-1]
            if isinstance(split_value_obj, list):
                if len(split_value_obj) == 2:
                    split_delimiter = split_value_obj[0]
                    split_string = split_value_obj[1]
                    if not isinstance(split_delimiter, six.string_types):
                        message = 'Split delimiter has to be of type string for {0}'
                        matches.append(RuleMatch(
                            tree + [0], message.format('/'.join(map(str, tree)))))
                    if isinstance(split_string, dict):
                        if len(split_string) == 1:
                            for key, _ in split_string.items():
                                if key not in supported_functions:
                                    message = 'Fn::Split doesn\'t support the function {0} at {1}'
                                    matches.append(RuleMatch(
                                        tree + [key], message.format(key, '/'.join(map(str, tree)))))
                        else:
                            message = 'Split list of singular function or string for {0}'
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree)))))
                    elif not isinstance(split_string, six.string_types):
                        message = 'Split has to be of type string or valid function for {0}'
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Split should be an array of 2 for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = 'Split should be an array of 2 for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
