"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Length(CloudFormationLintRule):
    """Check if Length values are correct"""
    id = 'E1030'
    shortdesc = 'Length validation of parameters'
    description = 'Making sure Fn::Length is configured correctly'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-length.html'
    tags = ['functions', 'length']

    def match(self, cfn):
        has_language_extensions_transform = cfn.has_language_extensions_transform()
        matches = []

        fn_length_objects = cfn.search_deep_keys('Fn::Length')
        for fn_length_object in fn_length_objects:
            tree = fn_length_object[:-1]
            if not has_language_extensions_transform:
                message = 'Missing Transform: Declare the AWS::LanguageExtensions Transform globally to enable use' \
                          ' of the intrinsic function Fn::Length at {0} '
                matches.append(RuleMatch(tree[:], message.format('/'.join(map(str, tree)))))
        return matches
