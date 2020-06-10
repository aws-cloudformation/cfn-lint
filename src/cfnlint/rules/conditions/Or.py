"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.conditions.common import check_condition_list


class Or(CloudFormationLintRule):
    """Check Or Condition Function Logic"""
    id = 'E8006'
    shortdesc = 'Check Fn::Or structure for validity'
    description = 'Check Fn::Or is a list of two elements'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-or'
    tags = ['functions', 'or']

    def match(self, cfn):
        return check_condition_list(cfn, 'Fn::Or')
