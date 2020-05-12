"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

from cfnlint.helpers import RESOURCE_SPECS


class StringSize(CloudFormationLintRule):
    """Check if a String has a length within the limit"""
    id = 'E3033'
    shortdesc = 'Check if a string has between min and max number of values specified'
    description = 'Check strings for its length between the minimum and maximum'
    source_url = 'https://github.com/awslabs/cfn-python-lint/blob/master/docs/cfn-resource-specification.md#allowedpattern'
    tags = ['resources', 'property', 'string', 'size']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def _check_string_length(self, value, path, **kwargs):
        """ """
        matches = []
        string_min = kwargs.get('string_min')
        string_max = kwargs.get('string_max')

        if isinstance(value, six.string_types):
            if not string_min <= len(value) <= string_max:
                message = 'String has to have length between {0} and {1} at {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(string_min, string_max, '/'.join(map(str, path))),
                    )
                )

        return matches

    def check(self, cfn, properties, specs, path):
        """Check itself"""
        matches = []
        for p_value, p_path in properties.items_safe(path[:]):
            for prop in p_value:
                if prop in specs:
                    value_type = specs.get(prop).get('Value', {}).get('ValueType', '')
                    if value_type:
                        if specs.get(prop).get('Type') == 'List':
                            property_type = specs.get(prop).get('PrimitiveItemType')
                        else:
                            property_type = specs.get(prop).get('PrimitiveType')

                        value_specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
                            'ValueTypes').get(value_type, {})

                        if value_specs.get('StringMax') and value_specs.get('StringMin'):
                            if property_type == 'String':
                                matches.extend(
                                    cfn.check_value(
                                        properties, prop, p_path,
                                        check_value=self._check_string_length,
                                        string_max=value_specs.get('StringMax'),
                                        string_min=value_specs.get('StringMin')
                                    )
                                )
        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'PropertyTypes').get(property_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'ResourceTypes').get(resource_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, specs, path))

        return matches
