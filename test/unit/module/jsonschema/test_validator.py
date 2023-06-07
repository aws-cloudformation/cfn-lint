"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import unittest
from collections import deque

from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.jsonschema.validators import CfnTemplateValidator


def fail(validator, errors, instance, schema):
    for each in errors:
        each.setdefault("message", "You told me to fail!")
        yield ValidationError(**each)


class TestCfnValidator(unittest.TestCase):
    def setUp(self):
        self.meta_schema = {"$id": "some://meta/schema"}
        self.validators = {"fail": fail}
        self.validator = CfnTemplateValidator({}).extend(
            validators=self.validators,
        )({})

    def test_iter_errors_successful(self):
        schema = {"fail": []}
        validator = self.validator.evolve(schema=schema)

        errors = list(validator.iter_errors("hello"))
        self.assertEqual(errors, [])

    def test_iter_errors_one_error(self):
        schema = {"fail": [{"message": "Whoops!"}]}
        validator = self.validator.evolve(schema=schema)

        expected_error = ValidationError(
            "Whoops!",
            instance="goodbye",
            schema=schema,
            validator="fail",
            validator_value=[{"message": "Whoops!"}],
            schema_path=deque(["fail"]),
        )

        errors = list(validator.iter_errors("goodbye"))
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]._contents(), expected_error._contents())

    def test_iter_errors_multiple_errors(self):
        schema = {
            "fail": [
                {"message": "First"},
                {"message": "Second!", "validator": "asdf"},
                {"message": "Third"},
            ],
        }
        validator = self.validator.evolve(schema=schema)

        errors = list(validator.iter_errors("goodbye"))
        self.assertEqual(len(errors), 3)


class TestValidationErrorMessages(unittest.TestCase):
    def message_for(self, instance, schema, **kwargs):
        cls = kwargs.pop("cls", CfnTemplateValidator)
        validator = cls(schema=schema).evolve(**kwargs)
        errors = list(validator.iter_errors(instance))
        self.assertTrue(errors, msg=f"No errors were raised for {instance!r}")
        self.assertEqual(
            len(errors),
            1,
            msg=f"Expected exactly one error, found {errors!r}",
        )
        return errors[0].message

    def test_single_type_failure(self):
        message = self.message_for(instance=[], schema={"type": "string"})
        self.assertEqual(message, "[] is not of type 'string'")

    def test_single_type_list_failure(self):
        message = self.message_for(instance=[], schema={"type": ["string"]})
        self.assertEqual(message, "[] is not of type 'string'")

    def test_multiple_type_failure(self):
        types = "string", "object"
        message = self.message_for(instance=[], schema={"type": list(types)})
        self.assertEqual(message, "[] is not of type 'string', 'object'")

    def test_minimum(self):
        message = self.message_for(instance=1, schema={"minimum": 2})
        self.assertEqual(message, "1 is less than the minimum of 2")

    def test_minimum_when_string(self):
        message = self.message_for(instance="1", schema={"minimum": 2})
        self.assertEqual(message, "'1' is less than the minimum of 2")

    def test_maximum(self):
        message = self.message_for(instance=1, schema={"maximum": 0})
        self.assertEqual(message, "1 is greater than the maximum of 0")

    def test_maximum_when_string(self):
        message = self.message_for(instance="1", schema={"maximum": 0})
        self.assertEqual(message, "'1' is greater than the maximum of 0")

    def test_dependencies_list(self):
        depend, on = "bar", "foo"
        schema = {"dependencies": {depend: [on]}}
        message = self.message_for(
            instance={"bar": 2},
            schema=schema,
            cls=CfnTemplateValidator,
        )
        self.assertEqual(message, "'foo' is a dependency of 'bar'")

    def test_dependencies_object(self):
        schema = {"dependencies": {"foo": {"required": ["bar"]}}}
        message = self.message_for(
            instance={"foo": True},
            schema=schema,
            cls=CfnTemplateValidator,
        )
        self.assertEqual(message, "'bar' is a required property")

    def test_additionalProperties_single_failure(self):
        schema = {"additionalProperties": False}
        message = self.message_for(instance={"foo": 2}, schema=schema)
        self.assertIn("('foo' was unexpected)", message)

    def test_additionalProperties_obj(self):
        schema = {"additionalProperties": {"type": "string"}}
        message = self.message_for(instance={"foo": []}, schema=schema)
        self.assertIn("[] is not of type 'string'", message)

    def test_additionalProperties_w_patternProperties(self):
        schema = {"additionalProperties": False, "patternProperties": {"^bar$": False}}
        message = self.message_for(instance={"foo": []}, schema=schema)
        self.assertIn("'foo' does not match any of the regexes: '^bar$'", message)

    def test_const(self):
        schema = {"const": 12}
        message = self.message_for(
            instance={"foo": "bar"},
            schema=schema,
        )
        self.assertIn("12 was expected", message)

    def test_enum(self):
        schema = {"enum": ["bar"]}
        message = self.message_for(
            instance="foo",
            schema=schema,
        )
        self.assertIn("'foo' is not one of ['bar']", message)

    def test_enum_int(self):
        schema = {"enum": [0]}
        message = self.message_for(
            instance=1,
            schema=schema,
        )
        self.assertIn("1 is not one of [0]", message)

    def test_invalid_format_default_message(self):
        schema = {"format": "date-time"}
        message = self.message_for(
            instance="bla",
            schema=schema,
        )

        self.assertIn(repr("bla"), message)
        self.assertIn(repr("date-time"), message)
        self.assertIn("is not a", message)

    def test_False_schema(self):
        message = self.message_for(
            instance="something",
            schema=False,
        )
        self.assertEqual(message, "False schema does not allow 'something'")

    def test_if_then(self):
        message = self.message_for(
            instance="a",
            schema={"if": {"type": "string"}, "then": False, "else": True},
        )
        self.assertEqual(message, "False schema does not allow 'a'")

    def test_if_else(self):
        message = self.message_for(
            instance=[],
            schema={"if": {"type": "string"}, "then": True, "else": False},
        )
        self.assertEqual(message, "False schema does not allow []")

    def test_items(self):
        message = self.message_for(
            instance=[[]],
            schema={"items": {"type": "string"}},
        )
        self.assertEqual(message, "[] is not of type 'string'")

    def test_items_list(self):
        message = self.message_for(
            instance=[[]],
            schema={"items": [{"type": "string"}]},
        )
        self.assertEqual(message, "[] is not of type 'string'")

    def test_multipleOf(self):
        message = self.message_for(
            instance=3,
            schema={"multipleOf": 2},
        )
        self.assertEqual(message, "3 is not a multiple of 2")

    def test_multipleOf_string(self):
        message = self.message_for(
            instance="3",
            schema={"multipleOf": 2},
        )
        self.assertEqual(message, "'3' is not a multiple of 2")

    def test_multipleOf_string_with_number(self):
        message = self.message_for(
            instance="3",
            schema={"multipleOf": 2.0},
        )
        self.assertEqual(message, "'3' is not a multiple of 2.0")

    def test_minItems(self):
        message = self.message_for(instance=[], schema={"minItems": 2})
        self.assertEqual(message, "[] is too short")

    def test_maxItems(self):
        message = self.message_for(instance=[1, 2, 3], schema={"maxItems": 2})
        self.assertEqual(message, "[1, 2, 3] is too long")

    def test_minLength(self):
        message = self.message_for(
            instance="",
            schema={"minLength": 2},
        )
        self.assertEqual(message, "'' is shorter than 2")

    def test_maxLength(self):
        message = self.message_for(
            instance="abc",
            schema={"maxLength": 2},
        )
        self.assertEqual(message, "'abc' is longer than 2")

    def test_not(self):
        message = self.message_for(
            instance=False,
            schema={"not": True},
        )
        self.assertEqual(message, "False should not be valid under True")

    def test_pattern(self):
        message = self.message_for(
            instance="bbb",
            schema={"pattern": "^a*$"},
        )
        self.assertEqual(message, "'bbb' does not match '^a*$'")

    def test_does_not_contain(self):
        message = self.message_for(
            instance=[],
            schema={"contains": {"type": "string"}},
        )
        self.assertEqual(
            message,
            "[] does not contain items matching the given schema",
        )

    def test_exclusiveMinimum(self):
        message = self.message_for(
            instance=3,
            schema={"exclusiveMinimum": 5},
        )
        self.assertEqual(
            message,
            "3 is less than or equal to the minimum of 5",
        )

    def test_exclusiveMaximum(self):
        message = self.message_for(instance=3, schema={"exclusiveMaximum": 2})
        self.assertEqual(
            message,
            "3 is greater than or equal to the maximum of 2",
        )

    def test_required_missing(self):
        message = self.message_for(instance={}, schema={"required": ["foo"]})
        self.assertEqual(message, "'foo' is a required property")

    def test_minProperties(self):
        message = self.message_for(instance={}, schema={"minProperties": 2})
        self.assertEqual(message, "{} does not have enough properties")

    def test_maxProperties(self):
        message = self.message_for(
            instance={"a": {}, "b": {}, "c": {}},
            schema={"maxProperties": 2},
        )
        self.assertEqual(
            message,
            "{'a': {}, 'b': {}, 'c': {}} has too many properties",
        )

    def test_patternProperties(self):
        message = self.message_for(
            instance={"foo": "bar"},
            schema={"patternProperties": {"^foo$": False}},
        )
        self.assertEqual(
            message,
            "False schema does not allow 'bar'",
        )

    def test_properties(self):
        message = self.message_for(
            instance={"foo": "bar"},
            schema={"properties": {"foo": False}},
        )
        self.assertEqual(
            message,
            "False schema does not allow 'bar'",
        )

    def test_propertyNames(self):
        message = self.message_for(
            instance={"foo": "bar"},
            schema={"propertyNames": {"pattern": "^bar$"}},
        )
        self.assertEqual(
            message,
            "'foo' does not match '^bar$'",
        )

    def test_oneOf_matches_none(self):
        message = self.message_for(instance={}, schema={"oneOf": [False]})
        self.assertEqual(
            message,
            "{} is not valid under any of the given schemas",
        )

    def test_oneOf_matches_too_many(self):
        message = self.message_for(instance={}, schema={"oneOf": [True, True]})
        self.assertEqual(message, "{} is valid under each of True, True")

    def test_allOf_matches_oneFalse(self):
        message = self.message_for(instance={}, schema={"allOf": [True, False]})
        self.assertEqual(message, "False schema does not allow {}")

    def test_anyOf_matches_none(self):
        message = self.message_for(instance={}, schema={"anyOf": [False, False]})
        self.assertEqual(message, "{} is not valid under any of the given schemas")

    def test_uniqueItems(self):
        message = self.message_for(
            instance=[1, 2, "1"],
            schema={"uniqueItems": True},
        )
        self.assertEqual(
            message,
            "[1, 2, '1'] has non-unique elements",
        )


class TestValidationTwoErrorMessages(unittest.TestCase):
    def message_for(self, instance, schema, **kwargs):
        cls = kwargs.pop("cls", CfnTemplateValidator)
        validator = cls(schema=schema).evolve(**kwargs)
        errors = list(validator.iter_errors(instance))
        self.assertTrue(errors, msg=f"No errors were raised for {instance!r}")
        self.assertEqual(
            len(errors),
            2,
            msg=f"Expected exactly two errors, found {errors!r}",
        )
        return [errors[0].message, errors[1].message]

    def test_additionalProperties_multiple_failure(self):
        schema = {"additionalProperties": False}
        messages = self.message_for(instance={"foo": 1, "bar": 2}, schema=schema)
        self.assertIn(
            "Additional properties are not allowed ('foo' was unexpected)", messages
        )
        self.assertIn(
            "Additional properties are not allowed ('bar' was unexpected)", messages
        )

    def test_allOf_matches_two_false(self):
        messages = self.message_for(instance={}, schema={"allOf": [True, False, False]})
        self.assertIn("False schema does not allow {}", messages[0])
        self.assertIn("False schema does not allow {}", messages[1])


class TestNoErrorMessage(unittest.TestCase):
    def no_error(self, instance, schema, **kwargs):
        cls = kwargs.pop("cls", CfnTemplateValidator)
        validator = cls(schema=schema).evolve(**kwargs)
        errors = list(validator.iter_errors(instance))
        self.assertFalse(errors, msg=f"Errors were raised for {instance!r}: {errors!r}")

    def test_single_type(self):
        self.no_error(instance="1", schema={"type": "string"})

    def test_single_type_when_int(self):
        self.no_error(instance=1, schema={"type": "string"})

    def test_single_type_with_list(self):
        self.no_error(instance="1", schema={"type": ["string"]})

    def test_multiple_type(self):
        types = "string", "object"
        self.no_error(instance="1", schema={"type": list(types)})

    def test_multiple_type_when_int(self):
        types = "string", "object"
        self.no_error(instance=1, schema={"type": list(types)})

    def test_minimum(self):
        self.no_error(instance=1, schema={"minimum": 0})

    def test_minimum_when_string(self):
        self.no_error(instance="1", schema={"minimum": 0})

    def test_minimum_when_wrong_type(self):
        self.no_error(instance="a", schema={"minimum": 0})

    def test_minimum_when_wrong_type_bool(self):
        self.no_error(instance=True, schema={"minimum": 0})

    def test_maximum(self):
        self.no_error(instance=0, schema={"maximum": 1})

    def test_maximum_when_string(self):
        self.no_error(instance="0", schema={"maximum": 1})

    def test_maximum_when_wrong_type(self):
        self.no_error(instance="a", schema={"maximum": 1})

    def test_maximum_when_wrong_type_bool(self):
        self.no_error(instance=True, schema={"maximum": 1})

    def test_additionalProperties_wrong_type(self):
        self.no_error(instance=[], schema={"additionalProperties": False})

    def test_dependencies_not_found(self):
        self.no_error(instance={"bar": True}, schema={"dependencies": {"foo": ["bar"]}})

    def test_dependencies_wrong_type(self):
        self.no_error(instance=[], schema={"dependencies": {"foo": ["bar"]}})

    def test_enum(self):
        self.no_error(instance=1, schema={"enum": ["1"]})

    def test_items_wrong_type(self):
        self.no_error(instance={}, schema={"items": {"type": "string"}})

    def test_multipleOf_when_string(self):
        self.no_error(
            instance="6",
            schema={"multipleOf": 2},
        )

    def test_multipleOf_when_number(self):
        self.no_error(
            instance=6.0,
            schema={"multipleOf": 2.0},
        )

    def test_multipleOf_wrong_type(self):
        self.no_error(
            instance="a",
            schema={"multipleOf": 2},
        )

    def test_multipleOf_wrong_type_bool(self):
        self.no_error(
            instance=True,
            schema={"multipleOf": 2},
        )

    def test_minItems_when_string(self):
        self.no_error(instance=[1, 2, 3], schema={"minItems": 2})

    def test_maxItems(self):
        self.no_error(
            instance=[
                1,
            ],
            schema={"maxItems": 2},
        )

    def test_minLength(self):
        self.no_error(
            instance="abc",
            schema={"minLength": 2},
        )

    def test_maxLength(self):
        self.no_error(
            instance="a",
            schema={"maxLength": 2},
        )

    def test_pattern(self):
        self.no_error(
            instance="aaa",
            schema={"pattern": "^a*$"},
        )

    def test_contains(self):
        self.no_error(
            instance=["a"],
            schema={"contains": {"type": "string"}},
        )

    def test_contains_wrong_type(self):
        self.no_error(instance={}, schema={"contains": {"type": "string"}})

    def test_exclusiveMinimum(self):
        self.no_error(
            instance=6,
            schema={"exclusiveMinimum": 5},
        )

    def test_exclusiveMinimum_string(self):
        self.no_error(instance="6", schema={"exclusiveMinimum": 5})

    def test_exclusiveMinimum_wrong_type(self):
        self.no_error(instance="a", schema={"exclusiveMinimum": 5})

    def test_exclusiveMinimum_wrong_type_bool(self):
        self.no_error(instance=True, schema={"exclusiveMinimum": 5})

    def test_exclusiveMaximum(self):
        self.no_error(instance=1, schema={"exclusiveMaximum": 2})

    def test_exclusiveMaximum_string(self):
        self.no_error(instance="1", schema={"exclusiveMaximum": 2})

    def test_exclusiveMaximum_wrong_type(self):
        self.no_error(instance="a", schema={"exclusiveMaximum": 2})

    def test_exclusiveMaximum_wrong_type_bool(self):
        self.no_error(instance=True, schema={"exclusiveMaximum": 2})

    def test_required(self):
        self.no_error(instance={"foo": "bar"}, schema={"required": ["foo"]})

    def test_minProperties(self):
        self.no_error(instance={"a": {}, "b": {}}, schema={"minProperties": 1})

    def test_minProperties_wrong_type(self):
        self.no_error(instance=[], schema={"minProperties": 1})

    def test_maxProperties(self):
        self.no_error(
            instance={"a": {}, "b": {}},
            schema={"maxProperties": 2},
        )

    def test_maxProperties_with_no_value(self):
        self.no_error(
            instance={"a": {}, "b": {"Ref": "AWS::NoValue"}},
            schema={"maxProperties": 2},
        )

    def test_maxProperties_wrong_type(self):
        self.no_error(instance=[], schema={"maxProperties": 1})

    def test_patternProperties_wrong_type(self):
        self.no_error(
            instance=[],
            schema={"patternProperties": {"^foo$": False}},
        )

    def test_properties_wrong_type(self):
        self.no_error(
            instance=[],
            schema={"properties": {"foo": False}},
        )

    def test_propertyNames_wrong_type(self):
        self.no_error(
            instance=[],
            schema={"propertyNames": {"pattern": "^[A-Za-z_][A-Za-z0-9_]*$"}},
        )

    def test_oneOf_matches_one(self):
        self.no_error(instance={}, schema={"oneOf": [True]})

    def test_oneOf_matches_just_one(self):
        self.no_error(instance={}, schema={"oneOf": [True, False]})

    def test_allOf_matches_all(self):
        self.no_error(instance={}, schema={"allOf": [True, True]})

    def test_anyOf_matches_all(self):
        self.no_error(instance={}, schema={"anyOf": [True, True]})

    def test_uniqueItems_wrong_type(self):
        self.no_error(
            instance={},
            schema={"uniqueItems": True},
        )
