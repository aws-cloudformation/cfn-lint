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
import sys
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
import cfnlint.helpers


class ValuePrimitiveType(CloudFormationLintRule):
    """Check if Resource PrimitiveTypes are correct"""
    id = 'E3012'
    shortdesc = 'Check resource properties values'
    description = 'Checks resource property values with Primitive Types for ' \
                  'values that match those types.'
    source_url = 'https://github.com/awslabs/cfn-python-lint/blob/master/docs/cfn-resource-specification.md#valueprimitivetype'
    tags = ['resources']

    def __init__(self, ):
        """Init """
        specs = cfnlint.helpers.RESOURCE_SPECS.get('us-east-1')
        self.property_specs = specs.get('PropertyTypes')
        self.resource_specs = specs.get('ResourceTypes')
        for resource_spec in self.resource_specs:
            self.resource_property_types.append(resource_spec)
        for property_spec in self.property_specs:
            self.resource_sub_property_types.append(property_spec)

    def check_primitive_type(self, value, item_type, path):
        """Chec item type"""
        matches = []

        if isinstance(value, dict) and item_type == 'Json':
            return matches
        if item_type in ['String']:
            if not isinstance(value, (str, six.text_type, six.string_types)):
                message = 'Property %s should be of type String' % ('/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))
        elif item_type in ['Boolean']:
            if not isinstance(value, (bool)):
                message = 'Property %s should be of type Boolean' % ('/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))
        elif item_type in ['Double']:
            if not isinstance(value, (float, int)):
                message = 'Property %s should be of type Double' % ('/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))
        elif item_type in ['Integer']:
            if not isinstance(value, (int)):
                message = 'Property %s should be of type Integer' % ('/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))
        elif item_type in ['Long']:
            if sys.version_info < (3,):
                integer_types = (int, long,)  # pylint: disable=undefined-variable
            else:
                integer_types = (int,)
            if not isinstance(value, integer_types):
                message = 'Property %s should be of type Long' % ('/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))
        elif isinstance(value, list):
            message = 'Property should be of type %s at %s' % (item_type, '/'.join(map(str, path)))
            matches.append(RuleMatch(path, message))

        return matches

    def check_value(self, value, path, **kwargs):
        """Check Value"""
        matches = []
        primitive_type = kwargs.get('primitive_type', {})
        item_type = kwargs.get('item_type', {})
        if item_type in ['Map']:
            if isinstance(value, dict):
                for map_key, map_value in value.items():
                    if not isinstance(map_value, dict):
                        matches.extend(self.check_primitive_type(map_value, primitive_type, path + [map_key]))
        else:
            matches.extend(self.check_primitive_type(value, primitive_type, path))

        return matches

    def check(self, cfn, properties, specs, path):
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
                    matches.extend(
                        cfn.check_value(
                            properties, prop, path,
                            check_value=self.check_value,
                            primitive_type=primitive_type,
                            item_type=item_type
                        )
                    )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        property_specs = self.property_specs.get(property_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, property_specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []
        resource_specs = self.resource_specs.get(resource_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, resource_specs, path))

        return matches
