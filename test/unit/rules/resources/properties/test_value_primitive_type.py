"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

import jsonschema

from cfnlint.rules.resources.properties.ValuePrimitiveType import (  # pylint: disable=E0401
    ValidationError,
    ValuePrimitiveType,
)


class TestResourceValuePrimitiveTypeCheckValue(BaseRuleTestCase):
    """Test Check Value for maps"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config["strict"] = False

    def test_strict_false(self):
        """Test Positive"""
        # Test Booleans
        self.assertEqual(
            self.rule._schema_check_primitive_type("True", ["boolean"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("False", ["boolean"]), True
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["boolean"]), False)
        # Test Strings
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["string"]), True)
        self.assertEqual(self.rule._schema_check_primitive_type(2, ["string"]), True)
        self.assertEqual(self.rule._schema_check_primitive_type(True, ["string"]), True)
        # Test Integer
        self.assertEqual(self.rule._schema_check_primitive_type("1", ["integer"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["integer"]), False
        )
        # Test Double
        self.assertEqual(self.rule._schema_check_primitive_type("1", ["number"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["number"]), True
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["number"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["number"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["number"]), False
        )
        # Test multiple types
        self.assertEqual(
            self.rule._schema_check_primitive_type("1", ["string", "integer"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["boolean", "integer"]),
            False,
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(1.34, ["boolean", "string"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.34", ["boolean", "number"]), True
        )

    def test_positive_strict(self):
        self.rule.config["strict"] = True
        # Test Booleans
        self.assertEqual(
            self.rule._schema_check_primitive_type("True", ["boolean"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("False", ["boolean"]), False
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["boolean"]), False)
        # Test Strings
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["string"]), False)
        self.assertEqual(self.rule._schema_check_primitive_type(2, ["string"]), False)
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["string"]), False
        )
        # Test Integer
        self.assertEqual(
            self.rule._schema_check_primitive_type("1", ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["integer"]), False
        )
        # Test Double
        self.assertEqual(self.rule._schema_check_primitive_type("1", ["number"]), False)
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["number"]), False
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["number"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["number"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["number"]), False
        )
        # Test multiple types
        self.assertEqual(
            self.rule._schema_check_primitive_type("1", ["string", "integer"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["boolean", "integer"]),
            False,
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(1.34, ["boolean", "string"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.34", ["boolean", "number"]), False
        )

        self.rule.config["strict"] = False


class TestResourceValuePrimitiveTypeJsonSchemaValidate(BaseRuleTestCase):
    """Test Primitive Value Types for Json Schema non strict"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config["strict"] = False

        self.validator = jsonschema._types.TypeChecker(
            {
                "any": jsonschema._types.is_any,
                "array": jsonschema._types.is_array,
                "boolean": jsonschema._types.is_bool,
                "integer": lambda checker, instance: (
                    jsonschema._types.is_integer(checker, instance)
                    or isinstance(instance, float)
                    and instance.is_integer()
                ),
                "object": jsonschema._types.is_object,
                "null": jsonschema._types.is_null,
                "number": jsonschema._types.is_number,
                "string": jsonschema._types.is_string,
            },
        )

    def test_validation(self):
        """Test Positive"""
        # sub is a string boolean
        self.assertEqual(
            len(
                list(
                    self.rule.type(
                        self.validator, ["string"], {"Fn::Sub": ["test"]}, {}
                    )
                )
            ),
            0,
        )
        # split is an array
        self.assertEqual(
            len(
                list(
                    self.rule.type(
                        self.validator, ["string"], {"Fn::Split": ["test"]}, {}
                    )
                )
            ),
            1,
        )
        # array type with split
        self.assertEqual(
            len(
                list(
                    self.rule.type(
                        self.validator, ["array"], {"Fn::Split": ["test"]}, {}
                    )
                )
            ),
            0,
        )
        # two types the second being valid
        self.assertEqual(
            len(
                list(
                    self.rule.type(
                        self.validator, ["string", "array"], {"Fn::Split": ["test"]}, {}
                    )
                )
            ),
            0,
        )
        # unknown function should return erro
        self.assertEqual(
            len(
                list(
                    self.rule.type(
                        self.validator, ["string"], {"Fn::ABC": ["test"]}, {}
                    )
                )
            ),
            1,
        )
