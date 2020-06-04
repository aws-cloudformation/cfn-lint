"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
        matches = []

        # Build the list of functions
        iftrees = cfn.search_deep_keys('Fn::If')

        # Get the conditions used in the functions
        for iftree in iftrees:
            ifs = iftree[-1]
            if isinstance(ifs, list):
                if_condition = ifs[0]
                if len(ifs) != 3:
                    message = 'Fn::If must be a list of 3 elements.'
                    matches.append(RuleMatch(
                        iftree[:-1], message
                    ))
                if not isinstance(if_condition, six.string_types):
                    message = 'Fn::If first element must be a condition and a string.'
                    matches.append(RuleMatch(
                        iftree[:-1] + [0], message
                    ))
            else:
                message = 'Fn::If must be a list of 3 elements.'
                matches.append(RuleMatch(
                    iftree[:-1], message
                ))

        return matches
