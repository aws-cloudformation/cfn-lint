"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class AttributeMismatch(CloudFormationLintRule):
    """Check DynamoDB Attributes"""
    id = 'E3039'
    shortdesc = 'AttributeDefinitions / KeySchemas mismatch'
    description = 'Verify the set of Attributes in AttributeDefinitions and KeySchemas match'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html'
    tags = ['resources', 'dynamodb']

    def __init__(self):
        """Init"""
        super(AttributeMismatch, self).__init__()
        self.resource_property_types = ['AWS::DynamoDB::Table']

    def check(self, properties, path, cfn):
        """Check itself"""
        matches = []
        keys = set()
        attributes = set()
        property_sets = cfn.get_object_without_conditions(properties)
        for property_set in property_sets:
            properties = property_set.get('Object')
            for attribute in properties.get('AttributeDefinitions'):
                attributes.add(attribute.get('AttributeName'))
            for key in properties.get('KeySchema'):
                keys.add(key.get('AttributeName'))
            if properties.get('GlobalSecondaryIndexes'):
                for index in properties.get('GlobalSecondaryIndexes'):
                    for key in index.get('KeySchema'):
                        keys.add(key.get('AttributeName'))
            if properties.get('LocalSecondaryIndexes'):
                for index in properties.get('LocalSecondaryIndexes'):
                    for key in index.get('KeySchema'):
                        keys.add(key.get('AttributeName'))
            if attributes != keys:
                message = 'The set of Attributes in AttributeDefinitions: {0} and KeySchemas: {1} must match at {2}'
                matches.append(RuleMatch(
                    path,
                    message.format(attributes, keys, '/'.join(map(str, path)))
                ))
        return matches

    def match_resource_properties(self, properties, _, path, cfn):
        """Match for sub properties"""
        matches = []
        matches.extend(self.check(properties, path, cfn))
        return matches
