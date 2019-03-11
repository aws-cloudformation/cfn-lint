"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import json
import six
import pkg_resources
from testlib.testcase import BaseTestCase


class TestPatchedSpecs(BaseTestCase):
    """Test Patched spec files """
    def setUp(self):
        """ SetUp template object"""

        filename = '../../src/cfnlint/data/CloudSpecs/us-east-1.json'

        filename = pkg_resources.resource_filename(
            __name__,
            filename
        )

        with open(filename) as fp:
            self.spec = json.load(fp)

    def test_resource_type_values(self):
        """Test Resource Type Value"""
        for r_name, r_values in self.spec.get('ResourceTypes').items():
            for p_name, p_values in r_values.get('Properties').items():
                p_value_type = p_values.get('Value', {}).get('ValueType')
                if p_value_type:
                    self.assertIn(p_value_type, self.spec.get('ValueTypes'), 'ResourceType: %s, Property: %s' % (r_name, p_name))
                    # List Value if a singular value is set and the type is List
                    if p_values.get('Type') == 'List':
                        p_list_value_type = p_values.get('Value', {}).get('ListValueType')
                        if p_list_value_type:
                            self.assertIn(p_list_value_type, self.spec.get('ValueTypes'), 'ResourceType: %s, Property: %s' % (r_name, p_name))

    def test_property_type_values(self):
        """Test Property Type Values"""
        def _test_property_type_values(values, r_name, p_name):
            p_value_type = values.get('Value', {}).get('ValueType')
            if p_value_type:
                self.assertIn(p_value_type, self.spec.get('ValueTypes'), 'PropertyType: %s, Property: %s' % (r_name, p_name))
                # List Value if a singular value is set and the type is List
                if values.get('Type') == 'List':
                    p_list_value_type = values.get('Value', {}).get('ListValueType')
                    if p_list_value_type:
                        self.assertIn(p_list_value_type, self.spec.get('ValueTypes'), 'ResourceType: %s, Property: %s' % (r_name, p_name))

        for r_name, r_values in self.spec.get('PropertyTypes').items():
            if r_values.get('Properties') is None:
                _test_property_type_values(r_values, r_name, '')
            else:
                for p_name, p_values in r_values.get('Properties', {}).items():
                    _test_property_type_values(p_values, r_name, p_name)

    def _test_sub_properties(self, resource_name, v_propertyname, v_propertyvalues):
        property_types = self.spec.get('PropertyTypes').keys()
        if 'PrimitiveType' not in v_propertyvalues and 'PrimitiveItemType' not in v_propertyvalues:
            v_propertytype = ''
            if 'ItemType' in v_propertyvalues:
                v_propertytype = v_propertyvalues['ItemType']
            elif 'Type' in v_propertyvalues:
                v_propertytype = v_propertyvalues['Type']

            v_subproperty_type = str.format('{0}.{1}', resource_name, v_propertytype)

            property_exists = False
            if v_subproperty_type in property_types:
                property_exists = True
            elif v_propertytype in property_types:
                # Special: There is a "Tag" Property type that's used as a "CatchAll" mechanism for Tags,
                # If the subproperty is not found, check if it exists with the resource in the property
                property_exists = True

            self.assertEqual(property_exists, True, 'Specified property type {} not found for property {}'.format(v_subproperty_type, v_propertyname))

    def test_sub_properties(self):
        """Test Resource sub-Property definitions"""
        # Test properties from resources
        for v_name, v_values in self.spec.get('ResourceTypes').items():
            v_value_properties = v_values.get('Properties', {})
            for p_name, p_values in v_value_properties.items():
                self._test_sub_properties(v_name, p_name, p_values)

        # Test properties from subproperties
        for v_name, v_values in self.spec.get('PropertyTypes').items():
            # Grab the resource part from the subproperty
            resource_name = v_name.split('.', 1)[0]
            if resource_name:
                v_value_properties = v_values.get('Properties', {})
                if v_value_properties is None:
                    print(v_values)
                    self._test_sub_properties(resource_name, '', v_values)
                else:
                    for p_name, p_values in v_value_properties.items():
                        self._test_sub_properties(resource_name, p_name, p_values)

    def test_property_value_types(self):
        """Test Property Value Types"""
        for v_name, v_values in self.spec.get('ValueTypes').items():
            for p_name, p_values in v_values.items():
                self.assertIn(p_name, ['Ref', 'GetAtt', 'AllowedValues', 'AllowedPattern', 'AllowedPatternRegex'])
                if p_name == 'Ref':
                    self.assertIsInstance(p_values, dict, 'ValueTypes: %s, Type: %s' % (v_name, p_name))
                    for r_name, r_value in p_values.items():
                        self.assertIn(r_name, ['Resources', 'Parameters'], 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, r_name))
                        self.assertIsInstance(r_value, list, 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, r_name))
                        if r_name == 'Parameters':
                            for r_list_value in r_value:
                                self.assertIsInstance(r_list_value, six.string_types, 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, r_name))
                                self.assertIn(r_list_value, self.spec.get('ParameterTypes'), 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, r_name))
                        elif r_name == 'Resources':
                            for r_list_value in r_value:
                                self.assertIsInstance(r_list_value, six.string_types, 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, r_name))
                                self.assertIn(r_list_value, self.spec.get('ResourceTypes'), 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, r_name))

                elif p_name == 'GetAtt':
                    self.assertIsInstance(p_values, dict, 'ValueTypes: %s, Type: %s' % (v_name, p_name))
                    for g_name, g_value in p_values.items():
                        self.assertIsInstance(g_value, six.string_types, 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, g_name))
                        self.assertIn(g_name, self.spec.get('ResourceTypes'), 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, g_name))
                        self.assertIn(g_value, self.spec.get('ResourceTypes', {}).get(g_name, {}).get('Attributes', {}), 'ValueTypes: %s, Type: %s, Additional Type: %s' % (v_name, p_name, g_name))
                elif p_name == 'AllowedValues':
                    self.assertIsInstance(p_values, list)
                    for l_value in p_values:
                        self.assertIsInstance(l_value, (six.string_types, six.integer_types), 'ValueTypes: %s, Type: %s' % (v_name, p_name))

    def test_parameter_types(self):
        """Test Parameter Types"""
        aws_parameter_types = [
            'AWS::EC2::AvailabilityZone::Name',
            'AWS::EC2::Image::Id', 'AWS::EC2::Instance::Id', 'AWS::EC2::KeyPair::KeyName',
            'AWS::EC2::SecurityGroup::GroupName', 'AWS::EC2::SecurityGroup::Id', 'AWS::EC2::Subnet::Id',
            'AWS::EC2::Volume::Id', 'AWS::EC2::VPC::Id', 'AWS::Route53::HostedZone::Id'
        ]
        valid_types = [
            'String', 'Number', 'List<Number>', 'CommaDelimitedList',
            'AWS::SSM::Parameter::Name', 'AWS::SSM::Parameter::Value<String>',
            'AWS::SSM::Parameter::Value<List<String>>', 'AWS::SSM::Parameter::Value<CommaDelimitedList>',
        ]
        for aws_parameter_type in aws_parameter_types:
            valid_types.append(aws_parameter_type)
            valid_types.append('List<%s>' % aws_parameter_type)
            valid_types.append('AWS::SSM::Parameter::Value<%s>' % aws_parameter_type)
            valid_types.append('AWS::SSM::Parameter::Value<List<%s>>' % aws_parameter_type)

        for v_name, v_values in self.spec.get('ParameterTypes').items():
            self.assertIsInstance(v_values, list, 'Parameter Type: %s' % (v_name))
