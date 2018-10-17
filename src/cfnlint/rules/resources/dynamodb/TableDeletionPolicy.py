"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


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
