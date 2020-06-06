"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.conditions.common import check_condition_list


class And(CloudFormationLintRule):
    """Check And Condition Function Logic"""
    id = 'E8004'
    shortdesc = 'Check Fn::And structure for validity'
    description = 'Check Fn::And is a list of two elements'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-and'
    tags = ['functions', 'and']

    def match(self, cfn):
        return check_condition_list(cfn, 'Fn::And')
