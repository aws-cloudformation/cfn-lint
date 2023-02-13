"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import unittest

from cfnlint.jsonschema.validator import CfnValidator


class TestValidators(unittest.TestCase):
    """Test JSON Schema validators"""

    def run_validation(self, instance, schema, *args, **kwargs):
        cls = kwargs.pop("cls", CfnValidator)
        validator = cls(schema, *args, **kwargs)
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

    def test_dependencies_array(self):
        depend, on = "bar", "foo"
        schema = {"dependencies": {depend: [on]}}
        message = self.message_for(
            instance={"bar": 2},
            schema=schema,
        )
        self.assertEqual(message, "'foo' is a dependency of 'bar'")

        self.no_error(instance={"bar": 2, "foo": 1}, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_dependencies_object(self):
        depend, on = "bar", "foo"
        schema = {"dependencies": {depend: {"properties": {on: {"type": "number"}}}}}
        message = self.message_for(
            instance={"bar": 2, "foo": "a"},
            schema=schema,
        )
        self.assertEqual(message, "'a' is not of type 'number'")

        self.no_error(instance={"bar": 2, "foo": 1}, schema=schema)

    def test_contains(self):
        schema = {"contains": {"type": "number"}}
        message = self.message_for(
            instance=["a"],
            schema=schema,
        )
        self.assertEqual(message, "None of ['a'] are valid under the given schema")

        self.no_error(instance=[1], schema=schema)
        # wrong type so no errors
        self.no_error(instance={}, schema=schema)

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

    def test_property_names(self):
        schema = {
            "propertyNames": {
                "pattern": "^bar$",
            },
        }
        message = self.message_for(
            instance={"foo": 2},
            schema=schema,
        )
        self.assertEqual(message, "'foo' does not match '^bar$'")

        self.no_error(instance={"bar": "a"}, schema=schema)
        # wrong type so no errors
        self.no_error(instance="a", schema=schema)

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

    def test_additional_items(self):
        first, additional = "foo", "bar"
        schema = {"items": [{"type": "string"}], "additionalItems": {"type": "string"}}
        message = self.message_for(instance=[first, 1], schema=schema)
        self.assertEqual(message, "1 is not of type 'string'")
        self.no_error(instance=[first, additional], schema=schema)

    def test_additional_items_false(self):
        schema = {"items": [{"type": "string"}], "additionalItems": False}
        message = self.message_for(instance=["a", 1], schema=schema)
        self.assertEqual(message, "Additional items are not allowed (1 was unexpected)")

        self.no_error(instance=["a"], schema=schema)
        # wrong type so no errors
        self.no_error(instance="a", schema=schema)

    def test_additional_properties_no_error(self):
        additional = "foo"
        schema = {"additionalProperties": True}

        self.no_error(instance={additional: 2}, schema=schema)

    def test_required(self):
        schema = {"properties": {"foo": {"type": "string"}}, "required": ["foo"]}
        message = self.message_for(instance={}, schema=schema)
        self.assertEqual(message, "'foo' is a required property")
        self.no_error(instance=[{"foo": "bar"}], schema=schema)

        # wrong type so no errors
        self.no_error(instance="a", schema=schema)

    def test_properties(self):
        schema = {"properties": {"foo": {"type": "string"}}}
        message = self.message_for(instance={"foo": 1}, schema=schema)
        self.assertEqual(message, "1 is not of type 'string'")
        self.no_error(instance=[{"foo": 1}], schema=schema)

        # wrong type so no errors
        self.no_error(instance="a", schema=schema)

    def test_const(self):
        schema = {"const": 12}
        message = self.message_for(
            instance={"foo": "bar"},
            schema=schema,
        )
        self.assertIn("12 was expected", message)

        self.no_error(instance=12, schema=schema)

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

    def test_multiple_of_number(self):
        schema = {"typeOf": "number", "multipleOf": 5}
        message = self.message_for(
            instance=6,
            schema=schema,
        )
        self.assertEqual(
            message,
            "6 is not a multiple of 5",
        )

        self.no_error(instance=5, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_multiple_of_float(self):
        schema = {"typeOf": "number", "multipleOf": 5.2}
        message = self.message_for(
            instance=6,
            schema=schema,
        )
        self.assertEqual(
            message,
            "6 is not a multiple of 5.2",
        )

        self.no_error(instance=10.4, schema=schema)

    def test_min_items(self):
        schema = {"minItems": 2}
        message = self.message_for(
            instance=["foo"],
            schema=schema,
        )
        self.assertEqual(
            message,
            "['foo'] is too short",
        )

        self.no_error(instance=["foo", "bar"], schema=schema)
        # wrong type so no errors
        self.no_error(instance="a", schema=schema)

    def test_max_items(self):
        schema = {"maxItems": 1}
        message = self.message_for(
            instance=["foo", "bar"],
            schema=schema,
        )
        self.assertEqual(
            message,
            "['foo', 'bar'] is too long",
        )

        self.no_error(instance=["foo"], schema=schema)
        # wrong type so no errors
        self.no_error(instance="a", schema=schema)

    def test_min_length(self):
        schema = {"minLength": 2}
        message = self.message_for(
            instance="a",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'a' is too short",
        )

        self.no_error(instance="foo", schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_max_length(self):
        schema = {"maxLength": 2}
        message = self.message_for(
            instance="foo",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'foo' is too long",
        )

        self.no_error(instance="a", schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_unique_items(self):
        schema = {"uniqueItems": True}
        message = self.message_for(
            instance=["foo", "foo"],
            schema=schema,
        )
        self.assertEqual(
            message,
            "['foo', 'foo'] has non-unique elements",
        )

        self.no_error(instance=["foo", "bar"], schema=schema)
        # wrong type so no errors
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

    def test_min_properties(self):
        schema = {"minProperties": 1}
        message = self.message_for(
            instance={},
            schema=schema,
        )
        self.assertEqual(
            message,
            "{} does not have enough properties",
        )

        self.no_error(instance={"foo": "bar"}, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_max_properties(self):
        schema = {"maxProperties": 1}
        message = self.message_for(
            instance={
                "foo": "foo",
                "bar": "bar",
            },
            schema=schema,
        )
        self.assertEqual(
            message,
            "{'foo': 'foo', 'bar': 'bar'} has too many properties",
        )

        self.no_error(instance={"foo": "bar"}, schema=schema)
        # wrong type so no errors
        self.no_error(instance=[], schema=schema)

    def test_not(self):
        schema = {
            "not": {
                "type": "string",
            }
        }
        message = self.message_for(
            instance="a",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'a' should not be valid under {'type': 'string'}",
        )

        self.no_error(instance=1, schema=schema)

    def test_one_of(self):
        schema = {
            "oneOf": [
                {"type": "string"},
                {"type": "number"},
            ]
        }
        message = self.message_for(
            instance=True,
            schema=schema,
        )
        self.assertEqual(
            message,
            "True is not valid under any of the given schemas",
        )

        self.no_error(instance="a", schema=schema)

    def test_one_of_multiple(self):
        schema = {
            "oneOf": [
                {"type": "string"},
                {"type": "string"},
            ]
        }
        message = self.message_for(
            instance="a",
            schema=schema,
        )
        self.assertEqual(
            message,
            "'a' is valid under each of {'type': 'string'}, {'type': 'string'}",
        )
