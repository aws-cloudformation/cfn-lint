"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

from cfnlint.helpers import RESOURCE_SPECS


class ListSize(CloudFormationLintRule):
    """Check if List has a size within the limit"""
    id = 'E3032'
    shortdesc = 'Check if a list has between min and max number of values specified'
    description = 'Check lists for the number of items in the list to validate they are between the minimum and maximum'
    source_url = 'https://github.com/awslabs/cfn-python-lint/blob/master/docs/cfn-resource-specification.md#allowedpattern'
    tags = ['resources', 'property', 'list', 'size']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def check_value(self, properties, path, property_name, cfn, value_specs):
        """Check Value"""
        matches = []

        # Get the Min and Max for a List
        list_min = value_specs.get('ListMin')
        list_max = value_specs.get('ListMax')

        if list_min is not None and list_max is not None:
            property_sets = cfn.get_object_without_conditions(properties)
            for property_set in property_sets:
                prop = property_set.get('Object').get(property_name)
                if isinstance(prop, list):
                    if not list_min <= len(prop) <= list_max:
                        if property_set['Scenario'] is None:
                            message = '{0} has to have between {1} and {2} items specified'
                            matches.append(
                                RuleMatch(
                                    path + [property_name],
                                    message.format(property_name, list_min, list_max),
                                )
                            )
                        else:
                            scenario_text = ' and '.join(['when condition "%s" is %s' % (
                                k, v) for (k, v) in property_set['Scenario'].items()])
                            message = '{0} has to have between {1} and {2} items specified when {3}'
                            matches.append(
                                RuleMatch(
                                    path + [property_name],
                                    message.format(property_name, list_min,
                                                   list_max, scenario_text),
                                )
                            )

        return matches

    def check(self, cfn, properties, specs, path):
        """Check itself"""
        matches = []
        for p_value, p_path in properties.items_safe(path[:]):
            for prop in p_value:
                if prop in specs:
                    value = specs.get(prop).get('Value', {})
                    if value:
                        value_type = value.get('ListValueType', '')
                        property_type = specs.get(prop).get('Type')
                        if property_type == 'List':
                            matches.extend(
                                self.check_value(
                                    p_value, p_path, prop, cfn,
                                    RESOURCE_SPECS.get(cfn.regions[0]).get(
                                        'ValueTypes').get(value_type, {})
                                )
                            )
        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'PropertyTypes').get(property_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'ResourceTypes').get(resource_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, specs, path))

        return matches
