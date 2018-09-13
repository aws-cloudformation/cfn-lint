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


class InterfaceConfiguration(CloudFormationLintRule):
    """Check if Metadata Interface Configuration are configured correctly"""
    id = 'E4001'
    shortdesc = 'Metadata Interface have appropriate properties'
    description = 'Metadata Interface properties are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html'
    tags = ['metadata']

    valid_keys = [
        'ParameterGroups',
        'ParameterLabels'
    ]

    def match(self, cfn):
        """Check CloudFormation Metadata Interface Configuration"""

        matches = []

        strinterface = 'AWS::CloudFormation::Interface'

        metadata_obj = cfn.template.get('Metadata', {})
        if metadata_obj:
            interfaces = metadata_obj.get(strinterface, {})
            if isinstance(interfaces, dict):
                for interface in interfaces:
                    if interface not in self.valid_keys:
                        message = 'Metadata Interface has invalid property {0}'
                        matches.append(RuleMatch(
                            ['Metadata', strinterface, interface],
                            message.format(interface)
                        ))
                parameter_groups = interfaces.get('ParameterGroups', [])
                for index, value in enumerate(parameter_groups):
                    for key in value:
                        if key not in ['Label', 'Parameters']:
                            message = 'Metadata Interface has invalid property {0}'
                            matches.append(RuleMatch(
                                ['Metadata', strinterface, 'ParameterGroups', index, key],
                                message.format(key)
                            ))

        return matches
