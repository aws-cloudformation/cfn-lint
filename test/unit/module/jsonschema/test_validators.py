"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import unittest

from jsonschema import Draft7Validator
from jsonschema.validators import extend

from cfnlint.jsonschema import _validators


class TestValidators(unittest.TestCase):
    """Test JSON Schema validators"""

    def run_validation(self, instance, schema, *args, **kwargs):
        # cls = kwargs.pop("cls", Draft7Validator)
        # validator = cls(schema, *args, **kwargs)
        validator = extend(
            validator=Draft7Validator,
            validators={
                "minimum": _validators.minimum,
                "maximum": _validators.maximum,
                "exclusiveMaximum": _validators.exclusiveMaximum,
                "exclusiveMinimum": _validators.exclusiveMinimum,
                "additionalProperties": _validators.additionalProperties,
                "enum": _validators.enum,
            },
        )(schema=schema)
        return list(validator.iter_errors(instance))

    def message_for(self, instance, schema, *args, **kwargs):
        errors = self.run_validation(instance, schema, *args, **kwargs)
        self.assertTrue(errors, msg=f"No errors were raised for {instance!r}")
        self.assertEqual(
            len(errors),
            1,
            msg=f"Expected exactly one error, found {errors!r}",
        )
        return errors[0].message

    def no_error(self, instance, schema, *args, **kwargs):
        errors = self.run_validation(instance, schema, *args, **kwargs)
        self.assertEqual(len(errors), 0)

    def test_pattern_properties(self):
        schema = {
            "patternProperties": {
                "^bar$": {"type": "string"},
            }
        }
        message = self.message_for(
            instance={"bar": 2},
            schema=schema,
        )
        self.assertEqual(message, "2 is not of type 'string'")

        self.no_error(instance={"bar": "a"}, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_additional_properties_single_failure(self):
        additional = "foo"
        schema = {"additionalProperties": False}

        message = self.message_for(instance={additional: 2}, schema=schema)
        self.assertEqual(
            message, "Additional properties are not allowed (foo unexpected)"
        )
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_additional_properties_multiple_failures(self):
        schema = {"additionalProperties": False}
        errors = self.run_validation(dict.fromkeys(["foo", "bar"]), schema)
        self.assertEqual(
            len(errors),
            2,
            msg=f"Expected exactly one error, found {errors!r}",
        )
        messages = [errors[0].message, errors[1].message]
        self.assertIn(
            "Additional properties are not allowed (bar unexpected)", messages
        )
        self.assertIn(
            "Additional properties are not allowed (foo unexpected)", messages
        )

    def test_additional_properties_type(self):
        additional = "foo"
        schema = {"additionalProperties": {"type": "string"}}
        message = self.message_for(instance={additional: 2}, schema=schema)
        self.assertEqual(message, "2 is not of type 'string'")
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_additional_properties_pattern_properties(self):
        additional = "foo"
        schema = {
            "additionalProperties": False,
            "patternProperties": {"^bar$": {"type": "string"}},
        }
        message = self.message_for(instance={additional: 2}, schema=schema)
        self.assertEqual(message, "'foo' does not match any of the regexes: '^bar$'")
        self.no_error(instance={"bar": "a"}, schema=schema)

    def test_additional_properties_no_error(self):
        additional = "foo"
        schema = {"additionalProperties": True}

        self.no_error(instance={additional: 2}, schema=schema)

    def test_exlusive_minimum(self):
        schema = {"exclusiveMinimum": 5}
        message = self.message_for(
            instance=3,
            schema=schema,
        )
        self.assertEqual(
            message,
            "3 is less than or equal to the minimum of 5",
        )

        self.no_error(instance=6, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_exlusive_minimum_string(self):
        schema = {"exclusiveMinimum": 5}
        message = self.message_for(
            instance="3",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'3' is less than or equal to the minimum of 5",
        )

    def test_exclusive_minimum_str_non_number(self):
        schema = {"exclusiveMinimum": 5}
        self.no_error(instance="A", schema=schema)

    def test_exlusive_maximum(self):
        schema = {"exclusiveMaximum": 5}
        message = self.message_for(
            instance=6,
            schema=schema,
        )
        self.assertEqual(
            message,
            "6 is greater than or equal to the maximum of 5",
        )

        self.no_error(instance=3, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_exlusive_maximum_string(self):
        schema = {"exclusiveMaximum": 5}
        message = self.message_for(
            instance="6",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'6' is greater than or equal to the maximum of 5",
        )

    def test_exclusive_maximum_str_non_number(self):
        schema = {"exclusiveMaximum": 5}
        self.no_error(instance="a", schema=schema)

    def test_minimum(self):
        schema = {"minimum": 5}
        message = self.message_for(
            instance=3,
            schema=schema,
        )
        self.assertEqual(
            message,
            "3 is less than the minimum of 5",
        )

        self.no_error(instance=5, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_minimum_string(self):
        schema = {"minimum": 5}
        message = self.message_for(
            instance="3",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'3' is less than the minimum of 5",
        )

    def test_minimum_str_non_number(self):
        schema = {"minimum": 5}
        self.no_error(instance="a", schema=schema)

    def test_maximum(self):
        schema = {"maximum": 5}
        message = self.message_for(
            instance=6,
            schema=schema,
        )
        self.assertEqual(
            message,
            "6 is greater than the maximum of 5",
        )

        self.no_error(instance=5, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_maximum_string(self):
        schema = {"maximum": 5}
        message = self.message_for(
            instance="6",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'6' is greater than the maximum of 5",
        )

    def test_maximum_str_non_number(self):
        schema = {"maximum": 5}
        self.no_error(instance="a", schema=schema)

    def test_enum(self):
        schema = {"enum": ["foo"]}
        message = self.message_for(
            instance="bar",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'bar' is not one of ['foo']",
        )

        self.no_error(instance="foo", schema=schema)

    def test_enum_number(self):
        schema = {"enum": [0]}
        message = self.message_for(
            instance=1,
            schema=schema,
        )
        self.assertEqual(
            message,
            "1 is not one of [0]",
        )

        self.no_error(instance=0, schema=schema)

    def test_enum_number_from_string(self):
        schema = {"enum": [0]}
        self.no_error(instance="0", schema=schema)

    def test_enum_string_from_number(self):
        schema = {"enum": ["10"]}
        self.no_error(instance=10, schema=schema)

        schema = {"enum": ["0"]}
        self.no_error(instance=0, schema=schema)


class TestValidatorsCfnType(unittest.TestCase):
    """Test JSON Schema validators"""

    def run_validation(self, instance, schema, *args, **kwargs):
        # cls = kwargs.pop("cls", Draft7Validator)
        # validator = cls(schema, *args, **kwargs)
        validator = extend(
            validator=Draft7Validator,
            validators={
                "minimum": _validators.minimum,
                "maximum": _validators.maximum,
                "exclusiveMaximum": _validators.exclusiveMaximum,
                "exclusiveMinimum": _validators.exclusiveMinimum,
                "additionalProperties": _validators.additionalProperties,
                "enum": _validators.enum,
                "type": _validators.cfn_type,
            },
        )(schema=schema)
        return list(validator.iter_errors(instance))

    def message_for(self, instance, schema, *args, **kwargs):
        errors = self.run_validation(instance, schema, *args, **kwargs)
        self.assertTrue(errors, msg=f"No errors were raised for {instance!r}")
        self.assertEqual(
            len(errors),
            1,
            msg=f"Expected exactly one error, found {errors!r}",
        )
        return errors[0].message

    def no_error(self, instance, schema, *args, **kwargs):
        errors = self.run_validation(instance, schema, *args, **kwargs)
        self.assertEqual(len(errors), 0)

    def test_cfn_type_object(self):
        schema = {"type": "string"}
        self.no_error(instance={"Ref": "AWS::Region"}, schema=schema)
        self.no_error(
            instance={"Fn::Join": [",", {"Fn::GetAzs": "us-east-1"}]}, schema=schema
        )
        self.no_error(instance={"Ref": "Unknown"}, schema=schema)

        message = self.message_for(
            instance={"Fn::GetAZs": "us-east-1"},
            schema=schema,
        )
        self.assertEqual(
            message,
            "{'Fn::GetAZs': 'us-east-1'} is not of type 'string'",
        )

        message = self.message_for(
            instance={"Foo": "Bar"},
            schema=schema,
        )
        self.assertEqual(
            message,
            "{'Foo': 'Bar'} is not of type 'string'",
        )

        message = self.message_for(
            instance={"Ref": "AWS::NotificationARNs"},
            schema=schema,
        )
        self.assertEqual(
            message,
            "{'Ref': 'AWS::NotificationARNs'} is not of type 'string'",
        )

    def test_cfn_type_list(self):
        schema = {"type": "array", "items": {"type": "string"}}
        self.no_error(instance={"Fn::GetAZs": "us-east-1"}, schema=schema)

        message = self.message_for(
            instance={"Ref": "AWS::Region"},
            schema=schema,
        )
        self.assertEqual(
            message,
            "{'Ref': 'AWS::Region'} is not of type 'array'",
        )

        message = self.message_for(
            instance={"Fn::Join": [",", {"Fn::GetAzs": "us-east-1"}]},
            schema=schema,
        )
        self.assertEqual(
            message,
            "{'Fn::Join': [',', {'Fn::GetAzs': 'us-east-1'}]} is not of type 'array'",
        )

    def test_cfn_type_number(self):
        schema = {"type": "number"}
        self.no_error(instance="1", schema=schema)

        message = self.message_for(
            instance="a",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'a' is not of type 'number'",
        )

    def test_cfn_type_integer(self):
        schema = {"type": "integer"}
        self.no_error(instance="1", schema=schema)

        message = self.message_for(
            instance=1.2,
            schema=schema,
        )
        self.assertEqual(
            message,
            "1.2 is not of type 'integer'",
        )

        message = self.message_for(
            instance="a",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'a' is not of type 'integer'",
        )

    def test_cfn_type_boolean(self):
        schema = {"type": "boolean"}
        self.no_error(instance="true", schema=schema)
        self.no_error(instance="false", schema=schema)

        message = self.message_for(
            instance="a",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'a' is not of type 'boolean'",
        )

    def test_cfn_type_if(self):
        schema = {"type": "integer"}
        self.no_error(instance={"Fn::If": ["Unknown", "3", 2]}, schema=schema)

        message = self.message_for(
            instance={"Fn::If": ["Unknown", "3", "a"]},
            schema=schema,
        )
        self.assertEqual(
            message,
            "'a' is not of type 'integer'",
        )
