"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.decode.node import list_node
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

    def _get_key_schema_attributes(self, key_schemas_sets):
        """ Get Key Schema attributes """
        keys = set()

        for properties, _ in key_schemas_sets:
            for key in properties:
                attribute_name = key.get_safe('AttributeName', type_t=six.string_types)
                if attribute_name:
                    keys.add(key.get('AttributeName'))
        return keys

    def _get_attribute_secondary(self, property_sets):
        """ Get the key schemas from secondary indexes """
        keys = set()

        for properties, _ in property_sets:
            for index in properties:
                keys = keys.union(
                    self._get_key_schema_attributes(
                        index.get_safe('KeySchema', list_node([], None, None), [], list)
                    )
                )

        return keys

    def check_property_set(self, property_set, path):
        """ Check a property set """
        matches = []
        properties = property_set.get('Object')

        keys = set()
        attributes = set()

        for attribute in properties.get('AttributeDefinitions', []):
            attribute_name = attribute.get('AttributeName')
            if isinstance(attribute_name, six.string_types):
                attributes.add(attribute.get('AttributeName'))
            else:
                self.logger.info('attribute definitions is not using just strings')
                return matches
        keys = keys.union(
            self._get_key_schema_attributes(
                properties.get_safe('KeySchema', list_node([], None, None), [], list)
            )
        )
        keys = keys.union(self._get_attribute_secondary(
            properties.get_safe('GlobalSecondaryIndexes', list_node([], None, None), path, list
                                )))  # pylint: disable=bad-continuation
        keys = keys.union(self._get_attribute_secondary(
            properties.get_safe('LocalSecondaryIndexes', list_node([], None, None), path, list
                                )))  # pylint: disable=bad-continuation

        if attributes != keys:
            message = 'The set of Attributes in AttributeDefinitions: {0} and KeySchemas: {1} must match at {2}'
            matches.append(RuleMatch(
                path,
                message.format(sorted(list(attributes)), sorted(
                    list(keys)), '/'.join(map(str, path)))
            ))

        return matches

    def check(self, properties, path, cfn):
        """Check itself"""
        matches = []

        property_sets = cfn.get_object_without_conditions(
            properties, ['AttributeDefinitions', 'KeySchema', 'GlobalSecondaryIndexes', 'LocalSecondaryIndexes'])
        for property_set in property_sets:
            matches.extend(self.check_property_set(property_set, path))
        return matches

    def match_resource_properties(self, properties, _, path, cfn):
        """Match for sub properties"""
        matches = []
        matches.extend(self.check(properties, path, cfn))
        return matches
