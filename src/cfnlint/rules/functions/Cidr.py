"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

from cfnlint.helpers import REGEX_CIDR


class Cidr(CloudFormationLintRule):
    """Check if Cidr values are correct"""
    id = 'E1024'
    shortdesc = 'Cidr validation of parameters'
    description = 'Making sure the function CIDR is a list with valid values'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-cidr.html'
    tags = ['functions', 'cidr']

    def check_parameter_count(self, cfn, parameter_name):
        """Check Count Parameter if used"""
        matches = []
        parameter_obj = cfn.get_parameters().get(parameter_name, {})
        if parameter_obj:
            tree = ['Parameters', parameter_name]
            parameter_type = parameter_obj.get('Type')
            if parameter_type == 'Number':
                max_value = parameter_obj.get('MaxValue')
                min_value = parameter_obj.get('MinValue')
                if (not min_value) or min_value < 1 or min_value > 256:
                    message = 'Parameter for Cidr count have MinValue between 1 and 256 at {0}'
                    matches.append(RuleMatch(
                        tree + ['MinValue'], message.format('/'.join(map(str, tree + ['MinValue'])))))
                if (not max_value) or max_value < 1 or max_value > 256:
                    message = 'Parameter for Cidr count have MaxValue between 1 and 256 at {0}'
                    matches.append(RuleMatch(
                        tree + ['MaxValue'], message.format('/'.join(map(str, tree + ['MaxValue'])))))
            else:
                message = 'Parameter for Cidr count have be of Type Number at {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))

        return matches

    def check_parameter_size_mask(self, cfn, parameter_name):
        """Check SizeMask Parameter if used"""
        matches = []
        parameter_obj = cfn.get_parameters().get(parameter_name, {})
        if parameter_obj:
            tree = ['Parameters', parameter_name]
            parameter_type = parameter_obj.get('Type')
            if parameter_type == 'Number':
                max_value = parameter_obj.get('MaxValue')
                min_value = parameter_obj.get('MinValue')
                if (not min_value) or min_value < 1 or min_value > 256:
                    message = 'Parameter for Cidr sizeMask have MinValue between 1 and ' \
                        '128 (for ipv6) and 32 (for ipv4) at {0}'
                    matches.append(RuleMatch(
                        tree + ['MinValue'], message.format('/'.join(map(str, tree + ['MinValue'])))))
                if (not max_value) or max_value < 1 or max_value > 256:
                    message = 'Parameter for Cidr count have MaxValue between 1 and ' \
                        '128 (for ipv6) and 32 (for ipv4) at {0}'
                    matches.append(RuleMatch(
                        tree + ['MaxValue'], message.format('/'.join(map(str, tree + ['MaxValue'])))))
            else:
                message = 'Parameter for Cidr count have be of Type Number at {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        matches = []

        cidr_objs = cfn.search_deep_keys('Fn::Cidr')

        supported_functions = [
            'Fn::FindInMap',
            'Fn::Select',
            'Ref',
            'Fn::GetAtt',
            'Fn::Sub',
            'Fn::ImportValue'
        ]

        count_parameters = []
        size_mask_parameters = []

        for cidr_obj in cidr_objs:
            cidr_value_obj = cidr_obj[-1]
            tree = cidr_obj[:-1]
            if isinstance(cidr_value_obj, list):
                if len(cidr_value_obj) in [2, 3]:
                    ip_block_obj = cidr_value_obj[0]
                    count_obj = cidr_value_obj[1]
                    if len(cidr_value_obj) == 3:
                        size_mask_obj = cidr_value_obj[2]
                    else:
                        size_mask_obj = None

                    if isinstance(ip_block_obj, dict):
                        if len(ip_block_obj) == 1:
                            for index_key, _ in ip_block_obj.items():
                                if index_key not in supported_functions:
                                    message = 'Cidr ipBlock should be Cidr Range, Ref, GetAtt, Sub or Select for {0}'
                                    matches.append(RuleMatch(
                                        tree[:] + [0], message.format('/'.join(map(str, tree[:] + [0])))))
                    elif isinstance(ip_block_obj, (six.text_type, six.string_types)):
                        if not re.match(REGEX_CIDR, ip_block_obj):
                            message = 'Cidr ipBlock should be a Cidr Range based string for {0}'
                            matches.append(RuleMatch(
                                tree[:] + [0], message.format('/'.join(map(str, tree[:] + [0])))))
                    else:
                        message = 'Cidr ipBlock should be a string for {0}'
                        matches.append(RuleMatch(
                            tree[:] + [0], message.format('/'.join(map(str, tree[:] + [0])))))

                    if isinstance(count_obj, dict):
                        if len(count_obj) == 1:
                            for index_key, index_value in count_obj.items():
                                if index_key not in supported_functions:
                                    message = 'Cidr count should be Int, Ref, or Select for {0}'
                                    matches.append(RuleMatch(
                                        tree[:] + [1], message.format('/'.join(map(str, tree[:] + [1])))))
                                if index_key == 'Ref':
                                    count_parameters.append(index_value)
                    elif not isinstance(count_obj, six.integer_types):
                        message = 'Cidr count should be a int for {0}'
                        extra_args = {'actual_type': type(count_obj).__name__, 'expected_type': six.integer_types[0].__name__}
                        matches.append(RuleMatch(
                            tree[:] + [1], message.format('/'.join(map(str, tree[:] + [1]))), **extra_args))

                    if isinstance(size_mask_obj, dict):
                        if len(size_mask_obj) == 1:
                            for index_key, index_value in size_mask_obj.items():
                                if index_key not in supported_functions:
                                    message = 'Cidr sizeMask should be Int, Ref, or Select for {0}'
                                    matches.append(RuleMatch(
                                        tree[:] + [2], message.format('/'.join(map(str, tree[:] + [2])))))
                                if index_key == 'Ref':
                                    size_mask_parameters.append(index_value)
                    elif not isinstance(size_mask_obj, six.integer_types):
                        message = 'Cidr sizeMask should be a int for {0}'
                        extra_args = {'actual_type': type(count_obj).__name__, 'expected_type': six.integer_types[0].__name__}
                        matches.append(RuleMatch(
                            tree[:] + [2], message.format('/'.join(map(str, tree[:] + [2]))), **extra_args))

                else:
                    message = 'Cidr should be a list of 2 or 3 elements for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = 'Cidr should be a list of 2 or 3 elements for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))

        for count_parameter in set(count_parameters):
            matches.extend(self.check_parameter_count(cfn, count_parameter))
        for size_mask_parameter in set(size_mask_parameters):
            matches.extend(self.check_parameter_size_mask(cfn, size_mask_parameter))

        return matches
