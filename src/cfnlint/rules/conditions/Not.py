"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.conditions.common import check_condition_list


class Not(CloudFormationLintRule):
    """Check Not Condition Function Logic"""
    id = 'E8005'
    shortdesc = 'Check Fn::Not structure for validity'
    description = 'Check Fn::Not is a list of one element'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-not'
    tags = ['functions', 'not']

    def match(self, cfn):
        return check_condition_list(cfn, 'Fn::Not')
