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


class Required(CloudFormationLintRule):
    """Check if Outputs have required properties"""
    id = 'E6002'
    shortdesc = 'Outputs have required properties'
    description = 'Making sure the outputs have required properties'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        outputs = cfn.template.get('Outputs', {})
        if outputs:
            for output_name, output_value in outputs.items():
                if 'Value' not in output_value:
                    message = 'Output {0} is missing property {1}'
                    matches.append(RuleMatch(
                        ['Outputs', output_name, 'Value'],
                        message.format(output_name, 'Value')
                    ))
                if 'Export' in output_value:
                    if 'Name' not in output_value['Export']:
                        message = 'Output {0} is missing property {1}'
                        matches.append(RuleMatch(
                            ['Outputs', output_name, 'Export'],
                            message.format(output_name, 'Name')
                        ))

        return matches
