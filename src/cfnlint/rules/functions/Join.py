"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import RESOURCE_SPECS, VALID_PARAMETER_TYPES_LIST


class Join(CloudFormationLintRule):
    """Check if Join values are correct"""
    id = 'E1022'
    shortdesc = 'Join validation of parameters'
    description = 'Making sure the join function is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-join.html'
    tags = ['functions', 'join']

    def __init__(self):
        """Initialize the rule"""
        super(Join, self).__init__()
        self.list_supported_functions = []
        self.singular_supported_functions = []
        for intrinsic_type, intrinsic_value in RESOURCE_SPECS.get('us-east-1').get('IntrinsicTypes').items():
            if 'List' in intrinsic_value.get('ReturnTypes', []):
                self.list_supported_functions.append(intrinsic_type)
            if 'Singular' in intrinsic_value.get('ReturnTypes', []):
                self.singular_supported_functions.append(intrinsic_type)

    def _get_parameters(self, cfn):
        """Get all Parameter Names"""
        results = {}
        parameters = cfn.template.get('Parameters', {})
        if isinstance(parameters, dict):
            for param_name, param_values in parameters.items():
                # This rule isn't here to check the Types but we need
                # something valid if it doesn't exist
                results[param_name] = param_values.get('Type', 'String')

        return results

    def _normalize_getatt(self, getatt):
        """ Normalize getatt into an array"""
        if isinstance(getatt, six.string_types):
            return getatt.split('.', 1)
        return getatt

    def _is_ref_a_list(self, parameter, template_parameters):
        """ Is a Ref a list """
        list_params = [
            'AWS::NotificationARNs',
        ]

        if parameter in template_parameters:
            if template_parameters.get(parameter) in VALID_PARAMETER_TYPES_LIST:
                return True
        if parameter in list_params:
            return True
        return False

    def _is_getatt_a_list(self, parameter, get_atts):
        """ Is a GetAtt a List """

        for resource, attributes in get_atts.items():
            for attribute_name, attribute_values in attributes.items():
                if resource == parameter[0] and attribute_name == '*':
                    if attribute_values.get('PrimitiveItemType'):
                        return 'FALSE'
                    if attribute_values.get('Type') == 'List':
                        return 'TRUE'
                    return 'UNKNOWN'
                if resource == parameter[0] and attribute_name == parameter[1]:
                    if attribute_values.get('Type') == 'List':
                        return 'TRUE'

        return 'FALSE'

    def _match_string_objs(self, join_string_objs, cfn, path):
        """ Check join list """

        matches = []

        template_parameters = self._get_parameters(cfn)
        get_atts = cfn.get_valid_getatts()

        if isinstance(join_string_objs, dict):
            if len(join_string_objs) == 1:
                for key, value in join_string_objs.items():
                    if key not in self.list_supported_functions:
                        message = 'Fn::Join unsupported function for {0}'
                        matches.append(RuleMatch(
                            path, message.format('/'.join(map(str, path)))))
                    elif key in ['Ref']:
                        if not self._is_ref_a_list(value, template_parameters):
                            message = 'Fn::Join must use a list at {0}'
                            matches.append(RuleMatch(
                                path, message.format('/'.join(map(str, path)))))
                    elif key in ['Fn::GetAtt']:
                        if self._is_getatt_a_list(self._normalize_getatt(value), get_atts) == 'FALSE':
                            message = 'Fn::Join must use a list at {0}'
                            matches.append(RuleMatch(
                                path, message.format('/'.join(map(str, path)))))
            else:
                message = 'Join list of values should be singular for {0}'
                matches.append(RuleMatch(
                    path, message.format('/'.join(map(str, path)))))
        elif not isinstance(join_string_objs, list):
            message = 'Join list of values for {0}'
            matches.append(RuleMatch(
                path, message.format('/'.join(map(str, path)))))
        else:
            for string_obj in join_string_objs:
                if isinstance(string_obj, dict):
                    if len(string_obj) == 1:
                        for key, value in string_obj.items():
                            if key not in self.singular_supported_functions:
                                message = 'Join unsupported function for {0}'
                                matches.append(RuleMatch(
                                    path, message.format('/'.join(map(str, path)))))
                            elif key in ['Ref']:
                                if self._is_ref_a_list(value, template_parameters):
                                    message = 'Fn::Join must not be a list at {0}'
                                    matches.append(RuleMatch(
                                        path, message.format('/'.join(map(str, path)))))
                            elif key in ['Fn::GetAtt']:
                                if self._is_getatt_a_list(self._normalize_getatt(value), get_atts) == 'TRUE':
                                    message = 'Fn::Join must not be a list at {0}'
                                    matches.append(RuleMatch(
                                        path, message.format('/'.join(map(str, path)))))
                    else:
                        message = 'Join list of values should be singular for {0}'
                        matches.append(RuleMatch(
                            path, message.format('/'.join(map(str, path)))))
                elif not isinstance(string_obj, six.string_types):
                    message = 'Join list of singular function or string for {0}'
                    matches.append(RuleMatch(
                        path, message.format('/'.join(map(str, path)))))

        return matches

    def match(self, cfn):
        matches = []

        join_objs = cfn.search_deep_keys('Fn::Join')

        for join_obj in join_objs:
            join_value_obj = join_obj[-1]
            path = join_obj[:-1]
            if isinstance(join_value_obj, list):
                if len(join_value_obj) == 2:
                    join_string = join_value_obj[0]
                    join_string_objs = join_value_obj[1]
                    if not isinstance(join_string, six.string_types):
                        message = 'Join string has to be of type string for {0}'
                        matches.append(RuleMatch(
                            path, message.format('/'.join(map(str, path)))))
                    matches.extend(self._match_string_objs(join_string_objs, cfn, path))
                else:
                    message = 'Join should be an array of 2 for {0}'
                    matches.append(RuleMatch(
                        path, message.format('/'.join(map(str, path)))))
            else:
                message = 'Join should be an array of 2 for {0}'
                matches.append(RuleMatch(
                    path, message.format('/'.join(map(str, path)))))

        return matches
