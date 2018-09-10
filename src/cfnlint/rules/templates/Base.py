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


class Base(CloudFormationLintRule):
    """Check Base Template Settings"""
    id = 'E1001'
    shortdesc = 'Basic CloudFormation Template Configuration'
    description = 'Making sure the basic CloudFormation template components are properly configured'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['base']

    required_keys = [
        'Resources'
    ]

    def match(self, cfn):
        """Basic Matching"""
        matches = []

        top_level = []
        for x in cfn.template:
            top_level.append(x)
            if x not in cfn.sections:
                message = 'Top level item {0} isn\'t valid'
                matches.append(RuleMatch([x], message.format(x)))

        for y in self.required_keys:
            if y not in top_level:
                message = 'Missing top level item {0} to file module'
                matches.append(RuleMatch([y], message.format(y)))

        return matches
