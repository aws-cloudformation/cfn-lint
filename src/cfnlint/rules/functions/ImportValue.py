"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class ImportValue(CloudFormationLintRule):
    """Check if ImportValue values are correct"""
    id = 'E1016'
    shortdesc = 'ImportValue validation of parameters'
    description = 'Making sure the ImportValue function is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-importvalue.html'
    tags = ['functions', 'importvalue']

    def match(self, cfn):
        matches = []

        iv_objs = cfn.search_deep_keys('Fn::ImportValue')

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::If',
            'Fn::Join',
            'Fn::Select',
            'Fn::Split',
            'Fn::Sub',
            'Ref'
        ]

        unsupported_locations = [
            'Conditions'
        ]

        for iv_obj in iv_objs:
            iv_value = iv_obj[-1]
            tree = iv_obj[:-1]
            if iv_obj[0] in unsupported_locations:
                message = 'ImportValue cannot be used inside {0} at {1}'
                matches.append(RuleMatch(
                    tree, message.format(iv_obj[0], '/'.join(map(str, tree[:-1])))))
            if isinstance(iv_value, dict):
                if len(iv_value) == 1:
                    for key, _ in iv_value.items():
                        if key not in supported_functions:
                            message = 'ImportValue should be using supported function for {0}'
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree[:-1])))))
                else:
                    message = 'ImportValue should have one mapping for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree[:-1])))))
            elif not isinstance(iv_value, str):
                message = 'ImportValue should have supported function or string for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
