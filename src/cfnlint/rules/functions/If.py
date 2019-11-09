"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class If(CloudFormationLintRule):
    """Check if Condition exists"""
    id = 'E1028'
    shortdesc = 'Check Fn::If structure for validity'
    description = 'Check Fn::If to make sure its valid.  Condition has to be a string.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-if'
    tags = ['functions', 'if']

    def match(self, cfn):
        """Check CloudFormation Conditions"""

        matches = []

        # Build the list of functions
        iftrees = cfn.search_deep_keys('Fn::If')

        # Get the conditions used in the functions
        for iftree in iftrees:
            if isinstance(iftree[-1], list):
                if_condition = iftree[-1][0]
            else:
                if_condition = iftree[-1]

            if not isinstance(if_condition, six.string_types):
                message = 'Fn::If first elements must be a condition and a string.'
                matches.append(RuleMatch(
                    iftree[:-1] + [0],
                    message.format(if_condition)
                ))

        return matches
