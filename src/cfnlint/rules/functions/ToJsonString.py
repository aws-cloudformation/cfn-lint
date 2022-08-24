"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.languageExtensions import LanguageExtensions


class ToJsonString(CloudFormationLintRule):
    """Check if ToJsonString values are correct"""
    id = 'E1031'
    shortdesc = 'ToJsonString validation of parameters'
    description = 'Making sure Fn::ToJsonString is configured correctly'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html'
    tags = ['functions', 'toJsonString']

    def match(self, cfn):
        has_language_extensions_transform = cfn.has_language_extensions_transform()
        unsupported_pseudo_parameters = [
            'AWS::NotificationARNs'
        ]

        matches = []
        intrinsic_function = 'Fn::ToJsonString'
        fn_toJsonString_objects = cfn.search_deep_keys(intrinsic_function)

        for fn_toJsonString_object in fn_toJsonString_objects:
            tree = fn_toJsonString_object[:-1]
            fn_toJsonString_object_value = fn_toJsonString_object[-1]
            LanguageExtensions.validate_transform_is_declared(self, has_language_extensions_transform, matches, tree,
                                                              intrinsic_function)
            LanguageExtensions.validate_type(self, fn_toJsonString_object_value, matches, tree, intrinsic_function)
            LanguageExtensions.validate_pseudo_parameters(self, fn_toJsonString_object_value, matches, tree,
                                                          unsupported_pseudo_parameters, intrinsic_function)
        return matches
