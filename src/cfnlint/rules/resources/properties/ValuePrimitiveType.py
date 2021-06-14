"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers


class ValuePrimitiveType(CloudFormationLintRule):
    """Check if Resource PrimitiveTypes are correct"""
    id = 'E3012'
    shortdesc = 'Check resource properties values'
    description = 'Checks resource property values with Primitive Types for values that match those types.'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#valueprimitivetype'
    tags = ['resources']

    strict_exceptions = {
        'AWS::CloudFormation::Stack': [
            'Parameters'
        ],
        'AWS::Lambda::Function.Environment': [
            'Variables'
        ]
    }

    def __init__(self):
        """Init"""
        super(ValuePrimitiveType, self).__init__()
        self.resource_specs = []
        self.property_specs = []
        self.config_definition = {
            'strict': {
                'default': True,
                'type': 'boolean'
            }
        }
        self.configure()

    def initialize(self, cfn):
        """Initialize the rule"""
        specs = cfnlint.helpers.RESOURCE_SPECS.get(cfn.regions[0])
        self.property_specs = specs.get('PropertyTypes')
        self.resource_specs = specs.get('ResourceTypes')
        for resource_spec in self.resource_specs:
            self.resource_property_types.append(resource_spec)
        for property_spec in self.property_specs:
            self.resource_sub_property_types.append(property_spec)

    def _value_check(self, value, path, item_type, strict_check, extra_args):
        """ Checks non strict """
        matches = []
        if not strict_check:
            try:
                if item_type in ['String']:
                    str(value)
                elif item_type in ['Boolean']:
                    if value not in ['True', 'true', 'False', 'false']:
                        message = 'Property %s should be of type %s' % (
                            '/'.join(map(str, path)), item_type)
                        matches.append(RuleMatch(path, message, **extra_args))
                elif item_type in ['Integer', 'Long', 'Double']:
                    if isinstance(value, bool):
                        message = 'Property %s should be of type %s' % (
                            '/'.join(map(str, path)), item_type)
                        matches.append(RuleMatch(path, message, **extra_args))
                    elif item_type in ['Integer']:
                        int(value)
                    elif item_type in ['Long']:
                        # Some times python will strip the decimals when doing a conversion
                        if isinstance(value, float):
                            message = 'Property %s should be of type %s' % (
                                '/'.join(map(str, path)), item_type)
                            matches.append(RuleMatch(path, message, **extra_args))
                        if sys.version_info < (3,):
                            long(value)  # pylint: disable=undefined-variable
                        else:
                            int(value)
                    else:  # has to be a Double
                        float(value)
            except Exception:  # pylint: disable=W0703
                message = 'Property %s should be of type %s' % ('/'.join(map(str, path)), item_type)
                matches.append(RuleMatch(path, message, **extra_args))
        else:
            message = 'Property %s should be of type %s' % ('/'.join(map(str, path)), item_type)
            matches.append(RuleMatch(path, message, **extra_args))

        return matches

    def check_primitive_type(self, value, item_type, path, strict_check):
        """Chec item type"""
        matches = []
        if isinstance(value, dict) and item_type == 'Json':
            return matches
        if item_type in ['String']:
            if not isinstance(value, (six.string_types)):
                extra_args = {'actual_type': type(value).__name__, 'expected_type': str.__name__}
                matches.extend(self._value_check(value, path, item_type, strict_check, extra_args))
        elif item_type in ['Boolean']:
            if not isinstance(value, (bool)):
                extra_args = {'actual_type': type(value).__name__, 'expected_type': bool.__name__}
                matches.extend(self._value_check(value, path, item_type, strict_check, extra_args))
        elif item_type in ['Double']:
            if not isinstance(value, (float, int)):
                extra_args = {'actual_type': type(value).__name__, 'expected_type': [
                    float.__name__, int.__name__]}
                matches.extend(self._value_check(value, path, item_type, strict_check, extra_args))
        elif item_type in ['Integer']:
            if not isinstance(value, (int)):
                extra_args = {'actual_type': type(value).__name__, 'expected_type': int.__name__}
                matches.extend(self._value_check(value, path, item_type, strict_check, extra_args))
        elif item_type in ['Long']:
            if sys.version_info < (3,):
                integer_types = (int, long,)  # pylint: disable=undefined-variable
            else:
                integer_types = (int,)
            if not isinstance(value, integer_types):
                extra_args = {'actual_type': type(value).__name__, 'expected_type': ' or '.join([
                    x.__name__ for x in integer_types])}
                matches.extend(self._value_check(value, path, item_type, strict_check, extra_args))
        elif isinstance(value, list):
            message = 'Property should be of type %s at %s' % (item_type, '/'.join(map(str, path)))
            extra_args = {'actual_type': type(value).__name__, 'expected_type': list.__name__}
            matches.append(RuleMatch(path, message, **extra_args))

        return matches

    def check_value(self, value, path, **kwargs):
        """Check Value"""
        matches = []
        primitive_type = kwargs.get('primitive_type', {})
        item_type = kwargs.get('item_type', {})
        strict_check = kwargs.get('non_strict', self.config['strict'])
        if item_type in ['Map']:
            if isinstance(value, dict):
                for map_key, map_value in value.items():
                    if not isinstance(map_value, dict):
                        matches.extend(self.check_primitive_type(
                            map_value, primitive_type, path + [map_key], strict_check))
        else:
            # some properties support primitive types and objects
            # skip in the case it could be an object and the value is a object
            if (item_type or primitive_type) and isinstance(value, dict):
                return matches
            matches.extend(self.check_primitive_type(value, primitive_type, path, strict_check))

        return matches

    def check(self, cfn, properties, specs, spec_type, path):
        """Check itself"""
        matches = []

        for prop in properties:
            if prop in specs:
                primitive_type = specs.get(prop).get('PrimitiveType')
                if not primitive_type:
                    primitive_type = specs.get(prop).get('PrimitiveItemType')
                if specs.get(prop).get('Type') in ['List', 'Map']:
                    item_type = specs.get(prop).get('Type')
                else:
                    item_type = None
                if primitive_type:
                    strict_check = self.config['strict']
                    if spec_type in self.strict_exceptions:
                        if prop in self.strict_exceptions[spec_type]:
                            strict_check = False
                    matches.extend(
                        cfn.check_value(
                            properties, prop, path,
                            check_value=self.check_value,
                            primitive_type=primitive_type,
                            item_type=item_type,
                            non_strict=strict_check,
                        )
                    )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        if self.property_specs.get(property_type, {}).get('Properties'):
            property_specs = self.property_specs.get(property_type, {}).get('Properties', {})
            matches.extend(self.check(cfn, properties, property_specs, property_type, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []
        resource_specs = self.resource_specs.get(resource_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, resource_specs, resource_type, path))

        return matches
