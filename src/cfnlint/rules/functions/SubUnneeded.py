"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class SubUnneeded(CloudFormationLintRule):
    """Check if Sub is using a variable"""
    id = 'W1020'
    shortdesc = 'Sub isn\'t needed if it doesn\'t have a variable defined'
    description = 'Checks sub strings to see if a variable is defined.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def _test_string(self, cfn, sub_string, tree):
        """Test if a string has appropriate parameters"""

        matches = []
        string_params = cfn.get_sub_parameters(sub_string)

        if not string_params:
            message = 'Fn::Sub isn\'t needed because there are no variables at {0}'
            matches.append(RuleMatch(
                tree, message.format('/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        matches = []

        sub_objs = cfn.transform_pre.get('Fn::Sub')

        for sub_obj in sub_objs:
            sub_value_obj = sub_obj[-1]
            tree = sub_obj[:-1]
            if isinstance(sub_value_obj, six.string_types):
                matches.extend(self._test_string(cfn, sub_value_obj, tree))
            elif isinstance(sub_value_obj, list):
                if len(sub_value_obj) == 2:
                    sub_string = sub_value_obj[0]
                    matches.extend(self._test_string(cfn, sub_string, tree + [0]))

        return matches
