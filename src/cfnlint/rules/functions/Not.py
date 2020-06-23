"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Not(CloudFormationLintRule):
    """Check if Not values are correct"""
    id = 'E1023'
    shortdesc = 'Validation NOT function configuration'
    description = 'Making sure that NOT functions are list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-not'
    tags = ['functions', 'not']

    def match(self, cfn):
        matches = []

        fnnots = cfn.search_deep_keys('Fn::Not')
        for fnnot in fnnots:
            if not isinstance(fnnot[-1], list):
                message = 'Function Not {0} should be a list'
                matches.append(RuleMatch(fnnot, message.format('/'.join(map(str, fnnot[:-2])))))

        return matches
