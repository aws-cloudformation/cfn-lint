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


class ImportValue(CloudFormationLintRule):
    """Check if ImportValue values are correct"""
    id = 'E1016'
    shortdesc = 'ImportValue validation of parameters'
    description = 'Making sure the function not is of list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-importvalue.html'
    tags = ['functions', 'importvalue']

    def match(self, cfn):
        """Check CloudFormation ImportValue"""

        matches = []

        iv_objs = cfn.search_deep_keys('Fn::ImportValue')

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::If',
            'Fn::Join',
            'Fn::Select',
            'Fn::Split',
            'Fn::Sub',
            'Ref'
        ]

        for iv_obj in iv_objs:
            iv_value = iv_obj[-1]
            tree = iv_obj[:-1]
            if isinstance(iv_value, dict):
                if len(iv_value) == 1:
                    for key, _ in iv_value.items():
                        if key not in supported_functions:
                            message = 'ImportValue should be using supported function for {0}'
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree[:-1])))))
                else:
                    message = 'ImportValue should have one mapping for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree[:-1])))))
            elif not isinstance(iv_value, six.string_types):
                message = 'ImportValue should have supported function or string for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
