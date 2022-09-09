"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class SubNotJoin(CloudFormationLintRule):
    """Check if Join is being used with no join characters"""

    id = 'I1022'
    shortdesc = 'Use Sub instead of Join'
    description = (
        'Prefer a sub instead of Join when using a join delimiter that is empty'
    )
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub', 'join']

    def _check_element(self, element):
        if isinstance(element, dict):
            if len(element) == 1:
                for key, value in element.items():
                    if key in ['Fn::Sub']:
                        if not isinstance(value, str):
                            return False
                    elif key not in ['Ref', 'Fn::GetAtt']:
                        return False

        return True

    def _check_elements(self, elements):
        for element in elements:
            if not self._check_element(element):
                return False

        return True

    def match(self, cfn):
        matches = []

        join_objs = cfn.search_deep_keys('Fn::Join')

        for join_obj in join_objs:
            if isinstance(join_obj[-1], list):
                join_operator = join_obj[-1][0]
                join_elements = join_obj[-1][1]
                if isinstance(join_operator, str):
                    if join_operator == '':
                        if isinstance(join_elements, list):
                            if self._check_elements(join_elements):
                                matches.append(
                                    RuleMatch(
                                        join_obj[0:-1],
                                        'Prefer using Fn::Sub over Fn::Join with an empty delimiter',
                                    )
                                )
        return matches
