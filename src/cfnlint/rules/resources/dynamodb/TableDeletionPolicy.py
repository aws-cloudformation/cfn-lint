"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class TableDeletionPolicy(CloudFormationLintRule):
    """Check Dynamo DB Deletion Policy"""
    id = 'I3011'
    shortdesc = 'Check DynamoDB tables have a set DeletionPolicy'
    description = 'The default action when removing a DynamoDB Table is to ' \
                  'delete it. This check requires you to specifically set a DeletionPolicy ' \
                  'and you know the risks'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html'
    tags = ['resources', 'dynamodb']

    def match(self, cfn):
        """Check CloudFormation DynamDB Tables"""
        matches = []

        resources = cfn.get_resources(resource_type=['AWS::DynamoDB::Table'])
        for r_name, r_values in resources.items():
            if not r_values.get('DeletionPolicy'):
                path = ['Resources', r_name]
                message = 'The default action on removal of a DynamoDB is to delete it. ' \
                          'Set a DeletionPolicy and specify either \'retain\' or \'delete\'.'
                matches.append(RuleMatch(path, message))

        return matches
