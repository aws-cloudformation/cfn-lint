"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.properties.ValuePrimitiveType import ValuePrimitiveType  # pylint: disable=E0401


class TestResourceValuePrimitiveType(BaseRuleTestCase):
    """Test Primitive Value Types"""

    def setUp(self):
        """Setup"""
        super(TestResourceValuePrimitiveType, self).setUp()
        self.collection.register(ValuePrimitiveType())

    success_templates = [
        'test/fixtures/templates/good/generic.yaml',
        'test/fixtures/templates/good/resource_properties.yaml',
        'test/fixtures/templates/good/resources/properties/primitive_types.yaml',
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_template_config(self):
        """Test strict false"""
        self.helper_file_rule_config(
            'test/fixtures/templates/good/resources/properties/value_non_strict.yaml',
            {'strict': False}, 0
        )
        self.helper_file_rule_config(
            'test/fixtures/templates/bad/resources/properties/value_non_strict.yaml',
            {'strict': False}, 4
        )

    def test_file_negative_nist_high_master(self):
        """Generic Test failure"""
        self.helper_file_negative('test/fixtures/templates/quickstart/nist_high_master.yaml', 6)

    def test_file_negative_nist_high_app(self):
        """Generic Test failure"""
        self.helper_file_negative('test/fixtures/templates/quickstart/nist_application.yaml', 53)

    def test_file_negative_nist_config_rules(self):
        """Generic Test failure"""
        self.helper_file_negative('test/fixtures/templates/quickstart/nist_config_rules.yaml', 2)

    def test_file_negative_generic(self):
        """Generic Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/generic.yaml', 7)


class TestResourceValuePrimitiveTypeNonStrict(BaseRuleTestCase):
    """Test Primitive Value Types"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config['strict'] = False

    def test_file_positive(self):
        """Test Positive"""
        # Test Booleans
        self.assertEqual(len(self.rule._value_check('True', ['test'], 'Boolean', {})), 0)
        self.assertEqual(len(self.rule._value_check('False', ['test'], 'Boolean', {})), 0)
        self.assertEqual(len(self.rule._value_check(1, ['test'], 'Boolean', {})), 1)
        # Test Strings
        self.assertEqual(len(self.rule._value_check(1, ['test'], 'String', {})), 0)
        self.assertEqual(len(self.rule._value_check(2, ['test'], 'String', {})), 0)
        self.assertEqual(len(self.rule._value_check(True, ['test'], 'String', {})), 0)
        # Test Integer
        self.assertEqual(len(self.rule._value_check('1', ['test'], 'Integer', {})), 0)
        self.assertEqual(len(self.rule._value_check('1.2', ['test'], 'Integer', {})), 1)
        self.assertEqual(len(self.rule._value_check(True, ['test'], 'Integer', {})), 1)
        self.assertEqual(len(self.rule._value_check('test', ['test'], 'Integer', {})), 1)
        # Test Double
        self.assertEqual(len(self.rule._value_check('1', ['test'], 'Double', {})), 0)
        self.assertEqual(len(self.rule._value_check('1.2', ['test'], 'Double', {})), 0)
        self.assertEqual(len(self.rule._value_check(1, ['test'], 'Double', {})), 0)
        self.assertEqual(len(self.rule._value_check(True, ['test'], 'Double', {})), 1)
        self.assertEqual(len(self.rule._value_check('test', ['test'], 'Double', {})), 1)
        # Test Long
        self.assertEqual(len(self.rule._value_check(str(65536 * 65536), ['test'], 'Long', {})), 0)
        self.assertEqual(len(self.rule._value_check('1', ['test'], 'Long', {})), 0)
        self.assertEqual(len(self.rule._value_check('1.2', ['test'], 'Long', {})), 1)
        self.assertEqual(len(self.rule._value_check(1.2, ['test'], 'Long', {})), 1)
        self.assertEqual(len(self.rule._value_check(65536 * 65536, ['test'], 'Long', {})), 0)
        self.assertEqual(len(self.rule._value_check(True, ['test'], 'Long', {})), 1)
        self.assertEqual(len(self.rule._value_check('test', ['test'], 'Long', {})), 1)
        # Test Unknown type doesn't return error
        self.assertEqual(len(self.rule._value_check(1, ['test'], 'Unknown', {})), 0)
        self.assertEqual(len(self.rule._value_check('1', ['test'], 'Unknown', {})), 0)
        self.assertEqual(len(self.rule._value_check(True, ['test'], 'Unknown', {})), 0)
