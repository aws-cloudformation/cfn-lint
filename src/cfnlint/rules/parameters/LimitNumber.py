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
from cfnlint.helpers import LIMITS


class LimitNumber(CloudFormationLintRule):
    """Check if maximum Parameter limit is exceeded"""
    id = 'E2010'
    shortdesc = 'Parameter limit not exceeded'
    description = 'Check the number of Parameters in the template is less' \
                  'than the upper limit'
    tags = ['base', 'parameters', 'limits']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = list()

        # Check number of parameters against the defined limit
        parameters = cfn.template.get('Parameters', {})
        if len(parameters) > LIMITS['parameters']['number']:
            message = 'Maximum number of parameters ({0}) exceeded'
            matches.append(RuleMatch(['Parameters'], message.format(LIMITS['parameters']['number'])))

        return matches
