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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Sub(CloudFormationLintRule):
    """Check if Sub values are correct"""
    id = 'E1019'
    shortdesc = 'Sub validation of parameters'
    description = 'Making sure the split function is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def _test_string(self, cfn, sub_string, parameters, tree):
        """Test if a string has appropriate parameters"""

        matches = []
        string_params = cfn.get_sub_parameters(sub_string)
        get_atts = cfn.get_valid_getatts()

        valid_pseudo_params = [
            'AWS::Region',
            'AWS::StackName',
            'AWS::URLSuffix',
            'AWS::StackId',
            'AWS::Region',
            'AWS::Partition',
            'AWS::NotificationARNs',
            'AWS::AccountId'
        ]

        valid_params = valid_pseudo_params
        valid_params.extend(cfn.get_parameter_names())
        valid_params.extend(cfn.get_resource_names())
        for key, _ in parameters.items():
            valid_params.append(key)

        for string_param in string_params:
            if isinstance(string_param, (six.string_types, six.text_type)):
                if string_param not in valid_params:
                    found = False
                    for resource, attributes in get_atts.items():
                        for attribute_name, _ in attributes.items():
                            if resource == string_param.split('.')[0] and attribute_name == '*':
                                found = True
                            elif (resource == string_param.split('.')[0] and
                                  attribute_name == '.'.join(string_param.split('.')[1:])):
                                found = True
                    if not found:
                        message = 'Parameter {0} for Fn::Sub not found at {1}'
                        matches.append(RuleMatch(
                            tree, message.format(string_param, '/'.join(map(str, tree)))))

        return matches

    def _test_parameters(self, parameters, tree):
        """Check parameters for appropriate configuration"""

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::GetAtt',
            'Fn::GetAZs',
            'Fn::ImportValue',
            'Fn::If',
            'Fn::Join',
            'Fn::Select',
            'Ref'
        ]

        matches = []
        for parameter_name, parameter_value_obj in parameters.items():
            param_tree = tree[:] + [parameter_name]
            if isinstance(parameter_value_obj, dict):
                if len(parameter_value_obj) == 1:
                    for key, _ in parameter_value_obj.items():
                        if key not in supported_functions:
                            message = 'Sub parameter should use a valid function for {0}'
                            matches.append(RuleMatch(
                                param_tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Sub parameter should be an object of 1 for {0}'
                    matches.append(RuleMatch(
                        param_tree, message.format('/'.join(map(str, tree)))))
            elif not isinstance(parameter_value_obj, six.string_types):
                message = 'Sub parameter should be an object of 1 or string for {0}'
                matches.append(RuleMatch(
                    param_tree, message.format('/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Join"""

        matches = []

        sub_objs = cfn.search_deep_keys('Fn::Sub')

        for sub_obj in sub_objs:
            sub_value_obj = sub_obj[-1]
            tree = sub_obj[:-1]
            if isinstance(sub_value_obj, six.string_types):
                matches.extend(self._test_string(cfn, sub_value_obj, {}, tree))
            elif isinstance(sub_value_obj, list):
                if len(sub_value_obj) == 2:
                    sub_string = sub_value_obj[0]
                    parameters = sub_value_obj[1]
                    if not isinstance(sub_string, six.string_types):
                        message = 'Subs first element should be of type string for {0}'
                        matches.append(RuleMatch(
                            tree + [0], message.format('/'.join(map(str, tree)))))
                    if not isinstance(parameters, dict):
                        message = 'Subs second element should be an object for {0}'
                        matches.append(RuleMatch(
                            tree + [1], message.format('/'.join(map(str, tree)))))
                    else:
                        matches.extend(self._test_string(cfn, sub_string, parameters, tree + [0]))
                        matches.extend(self._test_parameters(parameters, tree))
                else:
                    message = 'Sub should be an array of 2 for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = 'Sub should be a string or array of 2 items for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))

        return matches
