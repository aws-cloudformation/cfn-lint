"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.decode.node import sub_node


class SubUnneeded(CloudFormationLintRule):
    """Check if Sub is using a variable"""
    id = 'W1020'
    shortdesc = 'Sub isn\'t needed if it doesn\'t have a variable defined'
    description = 'Checks sub strings to see if a variable is defined.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def match(self, cfn):
        matches = []

        sub_objs = cfn.search_deep_class(sub_node)

        for sub_obj_tuple in sub_objs:
            path, sub_obj = sub_obj_tuple
            result_path = path[:] + ['Fn::Sub']
            if sub_obj.is_valid():
                if not sub_obj.get_string_vars():
                    message = 'Fn::Sub isn\'t needed because there are no variables at {0}'
                    matches.append(RuleMatch(
                        result_path, message.format('/'.join(map(str, result_path)))))

        return matches
