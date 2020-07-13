"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import bool_compare
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class NoEcho(CloudFormationLintRule):
    id = 'W4002'
    shortdesc = 'Check for NoEcho References'
    description = 'Check if there is a NoEcho enabled parameter referenced within a resources Metadata section'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html#parameters-section-structure-properties'
    tags = ['resources', 'NoEcho']

    def match(self, cfn):
        matches = []
        no_echo_params = []
        parameters = cfn.get_parameters()
        for parameter_name, parameter_value in parameters.items():
            noecho = parameter_value.get('NoEcho', default=False)
            if bool_compare(noecho, True):
                no_echo_params.append(parameter_name)

        if not no_echo_params:
            return no_echo_params

        resource_properties = cfn.get_resources()
        resource_dict = {key: resource_properties[key] for key in resource_properties if
                         isinstance(resource_properties[key], dict)}
        for resource_name, resource_values in resource_dict.items():
            resource_values = {key: resource_values[key] for key in resource_values if
                               isinstance(resource_values[key], dict)}
            metadata = resource_values.get('Metadata', {})
            if metadata is not None:
                for prop_name, properties in metadata.items():
                    if isinstance(properties, dict):
                        for property_value in properties.values():
                            for param in no_echo_params and no_echo_params:
                                if str(property_value).find(str(param)) > -1:
                                    path = ['Resources', resource_name, 'Metadata', prop_name]
                                    matches.append(RuleMatch(path, 'As the resource "metadata" section contains '
                                                                   'reference to a "NoEcho" parameter ' + str(param)
                                                             + ', CloudFormation will display the parameter value in '
                                                               'plaintext'))
        return matches
