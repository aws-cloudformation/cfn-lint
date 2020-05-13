"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class UpdateReplacePolicyDeletionPolicy(CloudFormationLintRule):
    """Check resources with UpdateReplacePolicy/DeletionPolicy have both"""
    id = 'W3011'
    shortdesc = 'Check resources with UpdateReplacePolicy/DeletionPolicy have both'
    description = 'Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html'
    tags = ['resources', 'updatereplacepolicy', 'deletionpolicy']

    def match(self, cfn):
        """Check resources with UpdateReplacePolicy/DeletionPolicy have both"""
        matches = []

        for r_name, r_values in cfn.get_resources().items():
            if r_values.get('Type') not in ['AWS::Lambda::Version', 'AWS::Lambda::LayerVersion']:
                # pylint: disable=too-many-boolean-expressions
                if r_values.get('DeletionPolicy') and r_values.get('DeletionPolicy') != 'Delete' and not r_values.get('UpdateReplacePolicy') or not r_values.get('DeletionPolicy') and r_values.get('UpdateReplacePolicy') and r_values.get('UpdateReplacePolicy') != 'Delete':
                    path = ['Resources', r_name]
                    message = 'Both UpdateReplacePolicy and DeletionPolicy are needed to protect %s from deletion' % '/'.join(path)
                    matches.append(RuleMatch(path, message))

        return matches
