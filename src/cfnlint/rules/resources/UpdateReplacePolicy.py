"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import valid_snapshot_types
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class UpdateReplacePolicy(CloudFormationLintRule):
    """Check Base Resource Configuration"""

    id = 'E3036'
    shortdesc = 'Check UpdateReplacePolicy values for Resources'
    description = 'Check that the UpdateReplacePolicy values are valid'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatereplacepolicy.html'
    tags = ['resources', 'updatereplacepolicy']

    def check_value(self, key, path, res_type, has_lang_exten_transform):
        """Check resource names for UpdateReplacePolicy"""
        matches = []

        valid_values = ['Delete', 'Retain', 'Snapshot']

        supported_functions = ['Fn::FindInMap', 'Fn::If', 'Ref']

        supported_functions_joined = ', '.join(supported_functions)

        if has_lang_exten_transform and isinstance(key, dict):
            if len(key) == 1:
                for index_key, _ in key.items():
                    if index_key not in supported_functions:
                        message = (
                            'UpdateReplacePolicy only supports one of the '
                            + supported_functions_joined
                            + ' intrinsic functions for {0}'
                        )
                        matches.append(
                            RuleMatch(path, message.format('/'.join(map(str, path))))
                        )
            else:
                message = 'UpdateReplacePolicy should have one mapping for {0}'
                matches.append(
                    RuleMatch(path, message.format('/'.join(map(str, path))))
                )
        else:
            if not isinstance(key, (str)):
                message = 'UpdateReplacePolicy values should be of string at {0}'
                matches.append(
                    RuleMatch(path, message.format('/'.join(map(str, path))))
                )
                return matches
            if key not in valid_values:
                message = 'UpdateReplacePolicy should be only one of {0} at {1}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            ', '.join(map(str, valid_values)), '/'.join(map(str, path))
                        ),
                    )
                )
            if key == 'Snapshot' and res_type not in valid_snapshot_types:
                message = 'UpdateReplacePolicy cannot be Snapshot for resources of type {0} at {1}'
                matches.append(
                    RuleMatch(path, message.format(res_type, '/'.join(map(str, path))))
                )

        return matches

    def match(self, cfn):
        matches = []

        resources = cfn.get_resources()

        for resource_name, resource_values in resources.items():
            updatereplace_policies = resource_values.get('UpdateReplacePolicy')
            if updatereplace_policies:
                path = ['Resources', resource_name, 'UpdateReplacePolicy']
                res_type = resource_values.get('Type')
                self.logger.debug(
                    'Validating UpdateReplacePolicy for %s base configuration',
                    resource_name,
                )
                if isinstance(updatereplace_policies, list):
                    message = 'Only one UpdateReplacePolicy allowed per resource at {0}'
                    matches.append(
                        RuleMatch(path, message.format('/'.join(map(str, path))))
                    )
                else:
                    has_lang_exten_transform = cfn.has_language_extensions_transform()
                    matches.extend(
                        self.check_value(
                            updatereplace_policies,
                            path,
                            res_type,
                            has_lang_exten_transform,
                        )
                    )

        return matches
