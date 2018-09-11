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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Not(CloudFormationLintRule):
    """Check if Not values are correct"""
    id = 'E1023'
    shortdesc = 'Validation NOT function configuration'
    description = 'Making sure that NOT functions are list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-not'
    tags = ['functions', 'not']

    def match(self, cfn):
        """Check CloudFormation GetAtt"""

        matches = []

        fnnots = cfn.search_deep_keys('Fn::Not')
        for fnnot in fnnots:
            if not isinstance(fnnot[-1], list):
                message = 'Function Not {0} should be a list'
                matches.append(RuleMatch(fnnot, message.format('/'.join(map(str, fnnot[:-2])))))

        return matches
