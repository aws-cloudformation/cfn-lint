"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class SubNotJoin(CloudFormationLintRule):
    """Check if Join is being used with no join characters"""
    id = 'I1022'
    shortdesc = 'Use Sub instead of Join'
    description = 'Prefer a sub instead of Join when using a join delimiter that is empty'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub', 'join']

    def match(self, cfn):
        matches = []

        join_objs = cfn.search_deep_keys('Fn::Join')

        for join_obj in join_objs:
            if isinstance(join_obj[-1], list):
                join_operator = join_obj[-1][0]
                if isinstance(join_operator, six.string_types):
                    if join_operator == '':
                        matches.append(RuleMatch(
                            join_obj[0:-1], 'Prefer using Fn::Sub over Fn::Join with an empty delimiter'))
        return matches
