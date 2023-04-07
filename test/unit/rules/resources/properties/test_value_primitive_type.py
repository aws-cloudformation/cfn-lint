"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.ValuePrimitiveType import (
    ValuePrimitiveType,  # pylint: disable=E0401
)


class TestResourceValuePrimitiveType(BaseRuleTestCase):
    """Test Primitive Value Types"""

    def setUp(self):
        """Setup"""
        super(TestResourceValuePrimitiveType, self).setUp()
        self.collection.register(ValuePrimitiveType())

    success_templates = [
        "test/fixtures/templates/good/generic.yaml",
        "test/fixtures/templates/good/resource_properties.yaml",
        "test/fixtures/templates/good/resources/properties/primitive_types.yaml",
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_bad_null_values(self):
        """Test strict false"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/primitive_types.yaml", 1
        )

    def test_template_config(self):
        """Test strict false"""
        self.helper_file_rule_config(
            "test/fixtures/templates/good/resources/properties/value_non_strict.yaml",
            {"strict": False},
            0,
        )
        self.helper_file_rule_config(
            "test/fixtures/templates/bad/resources/properties/value_non_strict.yaml",
            {"strict": False},
            4,
        )

    def test_bad_map_values(self):
        """Test strict false"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/primitive_types_map.yaml",
            2,
        )

    def test_file_negative_nist_high_main(self):
        """Generic Test failure"""
        self.helper_file_rule_config(
            "test/fixtures/templates/quickstart/nist_high_main.yaml",
            {"strict": True},
            6,
        )

    def test_file_negative_nist_high_app(self):
        """Generic Test failure"""
        self.helper_file_rule_config(
            "test/fixtures/templates/quickstart/nist_application.yaml",
            {"strict": True},
            53,
        )

    def test_file_negative_nist_config_rules(self):
        """Generic Test failure"""
        self.helper_file_rule_config(
            "test/fixtures/templates/quickstart/nist_config_rules.yaml",
            {"strict": True},
            2,
        )

    def test_file_negative_generic(self):
        """Generic Test failure"""
        self.helper_file_rule_config(
            "test/fixtures/templates/bad/generic.yaml", {"strict": True}, 7
        )


class TestResourceValuePrimitiveTypeNonStrict(BaseRuleTestCase):
    """Test Primitive Value Types"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config["strict"] = False

    def test_file_positive(self):
        """Test Positive"""
        # Test Booleans
        self.assertEqual(
            len(self.rule._value_check("True", ["test"], "Boolean", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("False", ["test"], "Boolean", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "Boolean", False, {})), 1
        )
        # Test Strings
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "String", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(2, ["test"], "String", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "String", False, {})), 0
        )
        # Test Integer
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Integer", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1.2", ["test"], "Integer", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Integer", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check("test", ["test"], "Integer", False, {})), 1
        )
        # Test Double
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Double", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1.2", ["test"], "Double", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "Double", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Double", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check("test", ["test"], "Double", False, {})), 1
        )
        # Test Long
        self.assertEqual(
            len(
                self.rule._value_check(str(65536 * 65536), ["test"], "Long", False, {})
            ),
            0,
        )
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Long", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1.2", ["test"], "Long", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check(1.2, ["test"], "Long", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check(65536 * 65536, ["test"], "Long", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Long", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check("test", ["test"], "Long", False, {})), 1
        )
        # Test Unknown type doesn't return error
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "Unknown", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Unknown", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Unknown", False, {})), 0
        )


class TestResourceValuePrimitiveTypeCheckValue(BaseRuleTestCase):
    """Test Check Value for maps"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config["strict"] = False

    def test_file_check_value_good_function(self):
        results = self.rule.check_value(
            {"key": {"Ref": ["Parameter"]}},
            [],
            primitive_type="String",
            item_type="Map",
        )
        self.assertEqual(len(results), 0)

    def test_file_check_value_is_string(self):
        results = self.rule.check_value(
            {"key": 1}, [], primitive_type="Integer", item_type="Map"
        )
        self.assertEqual(len(results), 0)

    def test_file_check_value_is_json(self):
        results = self.rule.check_value(
            {"key": {}}, [], primitive_type="Json", item_type="Map"
        )
        self.assertEqual(len(results), 0)

    def test_file_check_value_bad_function(self):
        results = self.rule.check_value(
            {"key": {"Func": ["Parameter"]}},
            [],
            primitive_type="Boolean",
            item_type="Map",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].message,
            "Use a valid function [Fn::Base64, Fn::Cidr, Fn::Contains, "
            "Fn::FindInMap, Fn::GetAtt, Fn::If, Fn::ImportValue, Fn::Join, Fn::Length, "
            "Fn::Select, Fn::Sub, Fn::ToJsonString, Ref] when "
            "providing a value of type [Boolean]",
        )

    def test_file_check_value_bad_object(self):
        results = self.rule.check_value(
            {"key": {"Func": ["Parameter"], "Func2": ["Parameter"]}},
            [],
            primitive_type="String",
            item_type="Map",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].message,
            "Use a valid function [Fn::Base64, Fn::Cidr, Fn::Contains, "
            "Fn::FindInMap, Fn::GetAtt, Fn::If, Fn::ImportValue, Fn::Join, Fn::Length, "
            "Fn::Select, Fn::Sub, Fn::ToJsonString, Ref] when "
            "providing a value of type [String]",
        )
