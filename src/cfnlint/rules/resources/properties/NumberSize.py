"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

from cfnlint.helpers import RESOURCE_SPECS


class NumberSize(CloudFormationLintRule):
    """Check if a Number has a length within the limit"""
    id = 'E3034'
    shortdesc = 'Check if a number is between min and max'
    description = 'Check numbers (integers and floats) for its value being between the minimum and maximum'
    source_url = 'https://github.com/awslabs/cfn-python-lint/blob/master/docs/cfn-resource-specification.md#allowedpattern'
    tags = ['resources', 'property', 'number', 'size']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def _check_number_value(self, value, path, **kwargs):
        """ Check if the value is in the given ranges"""
        matches = []
        number_min = kwargs.get('number_min')
        number_max = kwargs.get('number_max')

        # The Python types considered a "number"
        if sys.version_info < (3,):
            number_types = (float, int, long,)  # pylint: disable=undefined-variable
        else:
            number_types = (float, int,)

        if isinstance(value, six.string_types):
            try:
                value = float(value)
            except ValueError:
                message = 'Value has to be between {0} and {1} at {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(number_min, number_max, '/'.join(map(str, path))),
                    )
                )

        if isinstance(value, number_types):
            if not (number_min <= value <= number_max):
                message = 'Value has to be between {0} and {1} at {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(number_min, number_max, '/'.join(map(str, path))),
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
                        property_type = specs.get(prop).get('PrimitiveType')
                        value_specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
                            'ValueTypes').get(value_type, {})
                        if value_specs.get('NumberMax') is not None and value_specs.get('NumberMin') is not None:
                            if property_type in ['Integer', 'Double', 'Long', 'String']:
                                matches.extend(
                                    cfn.check_value(
                                        properties, prop, p_path,
                                        check_value=self._check_number_value,
                                        number_max=value_specs.get('NumberMax'),
                                        number_min=value_specs.get('NumberMin')
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
