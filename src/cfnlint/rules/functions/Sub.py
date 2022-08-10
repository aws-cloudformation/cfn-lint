"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import PSEUDOPARAMS, VALID_PARAMETER_TYPES_LIST
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Sub(CloudFormationLintRule):
    """Check if Sub values are correct"""
    id = 'E1019'
    shortdesc = 'Sub validation of parameters'
    description = 'Making sure the sub function is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def _test_string(self, cfn, sub_string, parameters, tree):
        """Test if a string has appropriate parameters"""

        matches = []
        string_params = cfn.get_sub_parameters(sub_string)

        for string_param in string_params:
            if isinstance(string_param, (str)):
                matches.extend(self._test_parameter(string_param, cfn, parameters, tree))

        return matches

    def _get_parameters(self, cfn):
        """Get all Parameter Names"""
        results = {}
        parameters = cfn.template.get('Parameters', {})
        if isinstance(parameters, dict):
            for param_name, param_values in parameters.items():
                # This rule isn't here to check the Types but we need
                # something valid if it doesn't exist
                if isinstance(param_values, dict):
                    results[param_name] = param_values.get('Type', 'String')

        return results

    def _test_parameters(self, parameters, cfn, tree):
        """Check parameters for appropriate configuration"""

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::GetAZs',
            'Fn::GetAtt',
            'Fn::If',
            'Fn::ImportValue',
            'Fn::Join',
            'Fn::Select',
            'Fn::Sub',
            'Ref',
        ]

        matches = []
        for parameter_name, parameter_value_obj in parameters.items():
            param_tree = tree[:] + [parameter_name]
            if isinstance(parameter_value_obj, dict):
                if len(parameter_value_obj) == 1:
                    for key, value in parameter_value_obj.items():
                        if key not in supported_functions:
                            message = 'Sub parameter should use a valid function for {0}'
                            matches.append(RuleMatch(
                                param_tree, message.format('/'.join(map(str, tree)))))
                        elif key in ['Ref']:
                            matches.extend(self._test_parameter(value, cfn, {}, tree))
                        elif key in ['Fn::GetAtt']:
                            if isinstance(value, list):
                                # Only test this if all the items are a string
                                if_all_strings = True
                                for v in value:
                                    if not isinstance(v, str):
                                        # skip things got too complex
                                        if_all_strings = False
                                if if_all_strings:
                                    matches.extend(self._test_parameter(
                                        '.'.join(value), cfn, {}, tree))
                            elif isinstance(value, str):
                                matches.extend(self._test_parameter(value, cfn, {}, tree))
                else:
                    message = 'Sub parameter should be an object of 1 for {0}'
                    matches.append(RuleMatch(
                        param_tree, message.format('/'.join(map(str, tree)))))
            elif isinstance(parameter_value_obj, list):
                message = 'Sub parameter value should be a string for {0}'
                matches.append(RuleMatch(
                    param_tree, message.format('/'.join(map(str, tree)))))

        return matches

    def _test_parameter(self, parameter, cfn, parameters, tree):
        """ Test a parameter """

        matches = []
        get_atts = cfn.get_valid_getatts()

        valid_params = list(PSEUDOPARAMS)
        valid_params.extend(cfn.get_resource_names())
        template_parameters = self._get_parameters(cfn)

        for key, _ in parameters.items():
            valid_params.append(key)

        if parameter not in valid_params:
            found = False
            if parameter in template_parameters:
                found = True
                if template_parameters.get(parameter) in VALID_PARAMETER_TYPES_LIST:
                    message = 'Fn::Sub cannot use list {0} at {1}'
                    matches.append(RuleMatch(
                        tree, message.format(parameter, '/'.join(map(str, tree)))))
            for resource, attributes in get_atts.items():
                for attribute_name, attribute_values in attributes.items():
                    if resource == parameter.split('.')[0]:
                        if attribute_name == '*':
                            found = True
                        elif attribute_name == '.'.join(parameter.split('.')[1:]):
                            if attribute_values.get('Type') == 'List':
                                message = 'Fn::Sub cannot use list {0} at {1}'
                                matches.append(RuleMatch(
                                    tree, message.format(parameter, '/'.join(map(str, tree)))))
                            found = True
                        else:
                            if attribute_name == parameter.split('.')[1] and attribute_values.get('Type') == 'Map':
                                found = True

            if not found:
                message = 'Parameter {0} for Fn::Sub not found at {1}'
                matches.append(RuleMatch(
                    tree, message.format(parameter, '/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        matches = []

        sub_objs = cfn.search_deep_keys('Fn::Sub')

        for sub_obj in sub_objs:
            sub_value_obj = sub_obj[-1]
            tree = sub_obj[:-1]
            if isinstance(sub_value_obj, str):
                matches.extend(self._test_string(cfn, sub_value_obj, {}, tree))
            elif isinstance(sub_value_obj, list):
                if len(sub_value_obj) == 2:
                    sub_string = sub_value_obj[0]
                    parameters = sub_value_obj[1]
                    if not isinstance(sub_string, str):
                        message = 'Subs first element should be of type string for {0}'
                        matches.append(RuleMatch(
                            tree + [0], message.format('/'.join(map(str, tree)))))
                    if not isinstance(parameters, dict):
                        message = 'Subs second element should be an object for {0}'
                        matches.append(RuleMatch(
                            tree + [1], message.format('/'.join(map(str, tree)))))
                    else:
                        matches.extend(self._test_string(cfn, sub_string, parameters, tree + [0]))
                        matches.extend(self._test_parameters(parameters, cfn, tree))
                else:
                    message = 'Sub should be an array of 2 for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            elif isinstance(sub_value_obj, dict):
                if len(sub_value_obj) == 1:
                    for key, _ in sub_value_obj.items():
                        if not key == 'Fn::Transform':
                            message = 'Sub should be a string or array of 2 items for {0}'
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Sub should be a string or array of 2 items for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = 'Sub should be a string or array of 2 items for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))

        return matches
