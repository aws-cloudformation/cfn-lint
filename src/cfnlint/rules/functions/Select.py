"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Select(CloudFormationLintRule):
    """Check if Select values are correct"""
    id = 'E1017'
    shortdesc = 'Select validation of parameters'
    description = 'Making sure the Select function is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html'
    tags = ['functions', 'select']

    def match(self, cfn):
        matches = []

        select_objs = cfn.search_deep_keys('Fn::Select')

        supported_functions = [
            'Fn::FindInMap',
            'Fn::GetAtt',
            'Fn::GetAZs',
            'Fn::If',
            'Fn::Split',
            'Fn::Cidr',
            'Ref'
        ]

        for select_obj in select_objs:
            select_value_obj = select_obj[-1]
            tree = select_obj[:-1]
            if isinstance(select_value_obj, list):
                if len(select_value_obj) == 2:
                    index_obj = select_value_obj[0]
                    list_of_objs = select_value_obj[1]
                    if isinstance(index_obj, dict):
                        if len(index_obj) == 1:
                            for index_key, _ in index_obj.items():
                                if index_key not in ['Ref', 'Fn::FindInMap', 'Fn::Select']:
                                    message = 'Select index should be an Integer or a function Ref or FindInMap for {0}'
                                    matches.append(RuleMatch(
                                        tree, message.format('/'.join(map(str, tree)))))
                    elif not isinstance(index_obj, int):
                        try:
                            int(index_obj)
                        except ValueError:
                            message = 'Select index should be an Integer or a function of Ref or FindInMap for {0}'
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree)))))
                    if isinstance(list_of_objs, dict):
                        if len(list_of_objs) == 1:
                            for key, _ in list_of_objs.items():
                                if key not in supported_functions:
                                    message = 'Select should use a supported function of {0}'
                                    matches.append(RuleMatch(
                                        tree, message.format(', '.join(map(str, supported_functions)))))
                        else:
                            message = 'Select should use a supported function of {0}'
                            matches.append(RuleMatch(
                                tree, message.format(', '.join(map(str, supported_functions)))))
                    elif not isinstance(list_of_objs, list):
                        message = 'Select should be an array of values for {0}'
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Select should be a list of 2 elements for {0}'
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = 'Select should be a list of 2 elements for {0}'
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
