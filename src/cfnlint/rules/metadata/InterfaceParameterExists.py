"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class InterfaceParameterExists(CloudFormationLintRule):
    """Check if Metadata Interface parameters exist"""
    id = 'W4001'
    shortdesc = 'Metadata Interface parameters exist'
    description = 'Metadata Interface parameters actually exist'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html'
    tags = ['metadata']

    valid_keys = [
        'ParameterGroups',
        'ParameterLabels'
    ]

    def match(self, cfn):
        """Check CloudFormation Metadata Parameters Exist"""

        matches = []

        strinterface = 'AWS::CloudFormation::Interface'
        parameters = cfn.get_parameter_names()
        metadata_obj = cfn.template.get('Metadata', {})
        if metadata_obj:
            interfaces = metadata_obj.get(strinterface, {})
            if isinstance(interfaces, dict):
                # Check Parameter Group Parameters
                paramgroups = interfaces.get('ParameterGroups', [])
                if isinstance(paramgroups, list):
                    for index, value in enumerate(paramgroups):
                        if 'Parameters' in value:
                            for paramindex, paramvalue in enumerate(value['Parameters']):
                                if paramvalue not in parameters:
                                    message = 'Metadata Interface parameter doesn\'t exist {0}'
                                    matches.append(RuleMatch(
                                        ['Metadata', strinterface, 'ParameterGroups',
                                         index, 'Parameters', paramindex],
                                        message.format(paramvalue)
                                    ))
                paramlabels = interfaces.get('ParameterLabels', {})
                if isinstance(paramlabels, dict):
                    for param in paramlabels:
                        if param not in parameters:
                            message = 'Metadata Interface parameter doesn\'t exist {0}'
                            matches.append(RuleMatch(
                                ['Metadata', strinterface, 'ParameterLabels', param],
                                message.format(param)
                            ))

        return matches
