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
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class SubNotJoin(CloudFormationLintRule):
    """Check if Join is being used with no join characters"""
    id = 'I1022'
    shortdesc = 'Use Sub instead of Join'
    description = 'Prefer a sub instead of Join when using a join delimiter that is empty'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub', 'join']

    def match(self, cfn):
        """Check CloudFormation """

        matches = []

        join_objs = cfn.search_deep_keys('Fn::Join')

        for join_obj in join_objs:
            if isinstance(join_obj[-1], list):
                join_operator = join_obj[-1][0]
                if isinstance(join_operator, six.string_types):
                    if join_operator == '':
                        matches.append(RuleMatch(
                            join_obj[0:-1], 'Prefer using Fn::Sub over Fn::Join with an empty delimiter'))
        return matches
