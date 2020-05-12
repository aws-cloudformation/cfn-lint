"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


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
