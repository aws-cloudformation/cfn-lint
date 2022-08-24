"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.languageExtensions import LanguageExtensions
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
        intrinsic_function = 'Fn::Length'
        matches = []

        fn_length_objects = cfn.search_deep_keys(intrinsic_function)
        for fn_length_object in fn_length_objects:
            tree = fn_length_object[:-1]
            LanguageExtensions.validate_transform_is_declared(self, has_language_extensions_transform, matches, tree, intrinsic_function)
            self.validate_type(fn_length_object, matches, tree)
            self.validate_ref(fn_length_object, matches, tree, cfn)
        return matches

    def validate_ref(self, fn_length_object, matches, tree, cfn):
        fn_length_value = fn_length_object[-1]
        if isinstance(fn_length_value, dict):
            if len(fn_length_value.keys()) != 1 or (list(fn_length_value.keys())[0] not in ['Ref', 'Fn::Split']):
                self.addMatch(matches, tree, 'Fn::Length expects either an array, a Ref to an array or Fn::Split, '
                                             'but found unexpected object under Fn::Length at {0}')
                return

            if 'Ref' in fn_length_value:
                if fn_length_value['Ref'] not in cfn.get_parameter_names():
                    self.addMatch(matches, tree, 'Fn::Length can only reference list parameters at {0}')
                else:
                    referenced_parameter = cfn.get_parameters().get(fn_length_value['Ref'])
                    parameter_type = referenced_parameter.get('Type')
                    if 'List' not in parameter_type:
                        self.addMatch(matches, tree, 'Fn::Length can only reference list parameters at {0}')

    def addMatch(self, matches, tree, message):
        matches.append(RuleMatch(tree[:], message.format('/'.join(map(str, tree)))))

    def validate_type(self, fn_length_object, matches, tree):
        fn_length_value = fn_length_object[-1]
        if not isinstance(fn_length_value, dict) and not isinstance(fn_length_value, list):
            message = 'Fn::Length needs a list or a reference to a list at {0}'
            matches.append(RuleMatch(tree[:], message.format('/'.join(map(str, tree)))))
