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


class LimitDescription(CloudFormationLintRule):
    """Check if maximum Output description size limit is exceeded"""
    id = 'E6012'
    shortdesc = 'Output description limit not exceeded'
    description = 'Check the size of Output description in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        outputs = cfn.template.get('Outputs', {})

        for output_name, output_value in outputs.items():
            description = output_value.get('Description')
            if description:
                path = ['Outputs', output_name, 'Description']
                if len(description) > LIMITS['outputs']['description']:
                    message = 'The length of output description ({0}) exceeds the limit ({1})'
                    matches.append(RuleMatch(path, message.format(len(description), LIMITS['outputs']['description'])))

        return matches
