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


class LimitName(CloudFormationLintRule):
    """Check if maximum Parameter name size limit is exceeded"""
    id = 'E2011'
    shortdesc = 'Parameter name limit not exceeded'
    description = 'Check the size of Parameter names in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        # Check number of parameters against the defined limit
        parameters = cfn.template.get('Parameters', {})

        for parameter_name in parameters:
            path = ['Parameters', parameter_name]
            if len(parameter_name) > LIMITS['parameters']['name']:
                message = 'The length of parameter name ({0}) exceeds the limit ({1})'
                matches.append(RuleMatch(path, message.format(len(parameter_name), LIMITS['parameters']['name'])))

        return matches
