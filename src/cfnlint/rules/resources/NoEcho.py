"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from ast import literal_eval
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class NoEcho(CloudFormationLintRule):
    """Check maximum Resource limit"""
    id = 'W4002'
    shortdesc = 'Check for NoEcho References'
    description = 'Check if there is a NoEcho enabled parameter referenced within a resource'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dne.html'
    tags = ['resources', 'NoEcho']

    def match(self, cfn):
        matches = []
        no_echo_params = []
        parameters = cfn.get_parameters()

        for parameter_name, parameter_value in parameters.items():
            parameter_properties = literal_eval(str(parameter_value))
            for parameter_properties_name, parameter_properties_value in parameter_properties.items():
                if parameter_properties_name == 'NoEcho' and parameter_properties_value is True:
                    no_echo_params.append(parameter_name)

        resource_properties = cfn.get_resources()

        for resource_name, resource_values in resource_properties.items():

            resource = literal_eval(str(resource_values))
            for key, value in resource.items():
                if key == 'Metadata':
                    metadata = literal_eval(str(value))
                    for prop_name, prop_value in metadata.items():
                        path = ['Resources', resource_name, 'Metadata', prop_name]
                        matches.append(RuleMatch(path, 'As the resource "metadata" section contains reference to a '
                                                       '"NoEcho" parameter (' + prop_value + '), CFN will display the '
                                                                                             'parameters description '
                                                                                             'in plaintext'))

        return matches
