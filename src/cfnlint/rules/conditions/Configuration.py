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


class Configuration(CloudFormationLintRule):
    """Check if Conditions are configured correctly"""
    id = 'E8001'
    shortdesc = 'Conditions have appropriate properties'
    description = 'Check if Conditions are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html'
    tags = ['conditions']

    condition_keys = [
        'Fn::And',
        'Fn::Equals',
        'Fn::If',
        'Fn::Not',
        'Fn::Or'
    ]

    def match(self, cfn):
        """Check CloudFormation Conditions"""

        matches = []

        conditions = cfn.template.get('Conditions', {})
        if conditions:
            for condname, condobj in conditions.items():
                if not isinstance(condobj, dict):
                    message = 'Condition {0} has invalid property'
                    matches.append(RuleMatch(
                        ['Conditions', condname],
                        message.format(condname)
                    ))
                else:
                    if len(condobj) != 1:
                        message = 'Condition {0} has to many intrinsic conditions'
                        matches.append(RuleMatch(
                            ['Conditions', condname],
                            message.format(condname)
                        ))

        return matches
