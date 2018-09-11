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


class SubUnneeded(CloudFormationLintRule):
    """Check if Sub is using a variable"""
    id = 'W1020'
    shortdesc = 'Sub isn\'t needed if it doesn\'t have a variable defined'
    description = 'Checks sub strings to see if a variable is defined.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def _test_string(self, cfn, sub_string, tree):
        """Test if a string has appropriate parameters"""

        matches = []
        string_params = cfn.get_sub_parameters(sub_string)

        if not string_params:
            message = 'Fn::Sub isn\'t needed because there are no variables at {0}'
            matches.append(RuleMatch(
                tree, message.format('/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Join"""

        matches = []

        sub_objs = cfn.search_deep_keys('Fn::Sub')

        for sub_obj in sub_objs:
            sub_value_obj = sub_obj[-1]
            tree = sub_obj[:-1]
            if isinstance(sub_value_obj, six.string_types):
                matches.extend(self._test_string(cfn, sub_value_obj, tree))
            elif isinstance(sub_value_obj, list):
                if len(sub_value_obj) == 2:
                    sub_string = sub_value_obj[0]
                    matches.extend(self._test_string(cfn, sub_string, tree + [0]))

        return matches
