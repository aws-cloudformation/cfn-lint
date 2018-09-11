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


class Base64(CloudFormationLintRule):
    """Check if Base64 values are correct"""
    id = 'E1021'
    shortdesc = 'Base64 validation of parameters'
    description = 'Making sure the function not is of list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-base64.html'
    tags = ['functions', 'base64']

    def match(self, cfn):
        """Check CloudFormation Base64"""

        matches = []

        base64_objs = cfn.search_deep_keys('Fn::Base64')
        for base64_obj in base64_objs:
            tree = base64_obj[:-1]
            value_obj = base64_obj[-1]
            if isinstance(value_obj, dict):
                if len(value_obj) == 1:
                    for key, _ in value_obj.items():
                        if key == 'Fn::Split':
                            message = 'Base64 needs a string at {0}'
                            matches.append(RuleMatch(
                                tree[:], message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Base64 needs a string not a map or list at {0}'
                    matches.append(RuleMatch(
                        tree[:], message.format('/'.join(map(str, tree)))))
            elif not isinstance(value_obj, six.string_types):
                message = 'Base64 needs a string at {0}'
                matches.append(RuleMatch(
                    tree[:], message.format('/'.join(map(str, tree)))))

        return matches
