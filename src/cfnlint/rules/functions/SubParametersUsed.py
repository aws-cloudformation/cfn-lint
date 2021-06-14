"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.decode.node import sub_node

class SubParametersUsed(CloudFormationLintRule):
    """Check if Sub Parameters are used"""
    id = 'W1019'
    shortdesc = 'Sub validation of parameters'
    description = 'Validate that Fn::Sub Parameters are used'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def match(self, cfn):
        matches = []

        sub_objs = cfn.search_deep_class(sub_node)

        for sub_obj_tuple in sub_objs:
            path, sub_obj = sub_obj_tuple
            result_path = path[:] + ['Fn::Sub', 1]
            sub_string_vars = sub_obj.get_string_vars()
            sub_vars = sub_obj.get_defined_vars()
            for sub_var in sub_vars:
                if sub_var not in sub_string_vars:
                    message = 'Parameter {0} not used in Fn::Sub at {1}'
                    matches.append(RuleMatch(
                        result_path + [sub_var], message.format(sub_var, '/'.join(map(str, result_path + [sub_var])))))

        return matches
