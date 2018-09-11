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
    """Check if maximum Output limit is exceeded"""
    id = 'E6010'
    shortdesc = 'Output limit not exceeded'
    description = 'Check the number of Outputs in the template is less' \
                  'than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        # Check number of outputs against the defined limit
        outputs = cfn.template.get('Outputs', {})
        if len(outputs) > LIMITS['outputs']['number']:
            message = 'The number of outputs ({0}) exceeds the limit ({1})'
            matches.append(RuleMatch(['Outputs'], message.format(len(outputs), LIMITS['outputs']['number'])))

        return matches
