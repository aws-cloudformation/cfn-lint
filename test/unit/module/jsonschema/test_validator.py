"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest.mock import patch

import pytest

from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.jsonschema.validators import CfnTemplateValidator


def fail(validator, errors, instance, schema):
    for each in errors:
        each.setdefault("message", "You told me to fail!")
        yield ValidationError(**each)


@pytest.fixture
def validator():
    validators = {"fail": fail}
    validator = CfnTemplateValidator({}).extend(
        validators=validators,
    )({})
    return validator


def _eq(self, other):
    return self.message == other.message


def _lt(self, other):
    return hash(self.message) < hash(other.message)


@pytest.mark.parametrize(
    "name,schema,instance,expected",
    [
        ("Success", {"fail": []}, "hello", []),
        (
            "One Error",
            {"fail": [{"message": "Whoops!"}]},
            "goodbye",
            [
                ValidationError(
                    "Whoops!",
                    instance="goodbye",
                    schema={"fail": [{"message": "Whoops!"}]},
                    validator="fail",
                    validator_value=[{"message": "Whoops!"}],
                    schema_path=deque(["fail"]),
                )
            ],
        ),
        (
            "Multiple Errors",
            {
                "fail": [
                    {"message": "First"},
                    {"message": "Second!", "validator": "asdf"},
                    {"message": "Third"},
                ]
            },
            "goodbye",
            [
                ValidationError(
                    "First",
                    instance="goodbye",
                    schema={"message": "First"},
                    validator="fail",
                    validator_value=[{"message": "Whoops!"}],
                    schema_path=deque(["fail"]),
                ),
                ValidationError(
                    "Second!",
                    instance="goodbye",
                    schema={"message": "Second!", "validator": "asdf"},
                    validator="asdf",
                    validator_value=[{"message": "Whoops!"}],
                    schema_path=deque(["fail"]),
                ),
                ValidationError(
                    "Third",
                    instance="goodbye",
                    schema={"message": "Third"},
                    validator="fail",
                    validator_value=[{"message": "Whoops!"}],
                    schema_path=deque(["fail"]),
                ),
            ],
        ),
    ],
)
def test_validator(name, schema, instance, expected, validator):
    validator = validator.evolve(schema=schema)
    errs = list(validator.iter_errors(instance))
    assert errs == expected, f"{name!r} returned {errs!r}"


@pytest.mark.parametrize(
    "name,schema,instance,expected",
    [
        (
            "Valid type single",
            {"type": "string"},
            "foo",
            [],
        ),
        (
            "Valid type single array",
            {"type": ["string"]},
            "foo",
            [],
        ),
        (
            "Valid type many in array",
            {"type": ["string", "object"]},
            "foo",
            [],
        ),
        (
            "Single type failure",
            {"type": "string"},
            [],
            [ValidationError("[] is not of type 'string'")],
        ),
        (
            "Multiple type failure",
            {"type": ["string", "object"]},
            [],
            [
                ValidationError(
                    "[] is not of type 'string', 'object'",
                )
            ],
        ),
        (
            "Multiple type failure",
            {"type": "string"},
            [],
            [ValidationError("[] is not of type 'string'")],
        ),
        (
            "valid minimum",
            {"minimum": 2},
            2,
            [],
        ),
        (
            "valid minimum with string",
            {"minimum": 2},
            "2",
            [],
        ),
        (
            "valid minimum with wrong type as string",
            {"minimum": 2},
            "a",
            [],
        ),
        (
            "valid minimum with wrong type",
            {"minimum": 2},
            {},
            [],
        ),
        (
            "valid minimum with wrong type boolean",
            {"minimum": 2},
            True,
            [],
        ),
        (
            "minimum",
            {"minimum": 2},
            1,
            [ValidationError("1 is less than the minimum of 2")],
        ),
        (
            "minimum with string",
            {"minimum": 2},
            "1",
            [
                ValidationError(
                    "'1' is less than the minimum of 2",
                )
            ],
        ),
        (
            "valid maximum",
            {"maximum": 2},
            "2",
            [],
        ),
        (
            "valid maximum with string",
            {"minimum": 2},
            "2",
            [],
        ),
        (
            "valid maximum with wrong type",
            {"maximum": 2},
            {},
            [],
        ),
        (
            "valid maximum with wrong type boolean",
            {"maximum": 2},
            True,
            [],
        ),
        (
            "valid maximum with wrong type as string",
            {"maximum": 2},
            "a",
            [],
        ),
        (
            "maximum",
            {"maximum": 0},
            1,
            [ValidationError("1 is greater than the maximum of 0")],
        ),
        (
            "maximum with string",
            {"maximum": 0},
            "1",
            [
                ValidationError(
                    "'1' is greater than the maximum of 0",
                )
            ],
        ),
        (
            "valid dependencies wrong type",
            {"dependencies": {"bar": ["foo"]}},
            [],
            [],
        ),
        (
            "dependencies list",
            {"dependencies": {"bar": ["foo"]}},
            {"bar": 2},
            [
                ValidationError(
                    "'foo' is a dependency of 'bar'",
                )
            ],
        ),
        (
            "valid dependencies when property not included",
            {"dependencies": {"bar": ["foo"]}},
            {"foo": 2},
            [],
        ),
        (
            "dependencies object",
            {"dependencies": {"foo": {"required": ["bar"]}}},
            {"foo": 2},
            [
                ValidationError(
                    "'bar' is a required property",
                )
            ],
        ),
        (
            "valid additionalProperties",
            {"additionalProperties": True},
            {"foo": "bar"},
            [],
        ),
        (
            "valid additionalProperties with wrong type",
            {"additionalProperties": False},
            [],
            [],
        ),
        (
            "additionalProperties false",
            {"additionalProperties": False},
            {"foo": 2},
            [
                ValidationError(
                    "Additional properties are not allowed ('foo' was unexpected)",
                )
            ],
        ),
        (
            "additionalProperties false",
            {"additionalProperties": False, "properties": {"foooooo": True}},
            {"foooooa": 2},
            [
                ValidationError(
                    (
                        "Additional properties are not allowed ('foooooa' "
                        "was unexpected. Did you mean 'foooooo'?)"
                    ),
                )
            ],
        ),
        (
            "additionalProperties object",
            {"additionalProperties": {"type": "string"}},
            {"foo": []},
            [
                ValidationError(
                    "[] is not of type 'string'",
                )
            ],
        ),
        (
            "additionalProperties with patternProperties",
            {"additionalProperties": False, "patternProperties": {"^bar$": False}},
            {"foo": []},
            [
                ValidationError(
                    "'foo' does not match any of the regexes: '^bar$'",
                )
            ],
        ),
        (
            "additionalProperties with multiple properties",
            {"additionalProperties": False},
            {"foo": [], "bar": []},
            [
                ValidationError(
                    "Additional properties are not allowed ('foo' was unexpected)",
                ),
                ValidationError(
                    "Additional properties are not allowed ('bar' was unexpected)",
                ),
            ],
        ),
        (
            "valid const",
            {"const": 12},
            12,
            [],
        ),
        (
            "const",
            {"const": 12},
            {"foo": "bar"},
            [
                ValidationError(
                    "12 was expected",
                )
            ],
        ),
        (
            "valid enum",
            {"enum": ["bar"]},
            "bar",
            [],
        ),
        (
            "enum",
            {"enum": ["bar"]},
            "foo",
            [
                ValidationError(
                    "'foo' is not one of ['bar']",
                    validator="enum",
                    schema_path=deque(["enum"]),
                )
            ],
        ),
        (
            "valid enum int",
            {"enum": [0]},
            "0",
            [],
        ),
        (
            "enum int",
            {"enum": [0]},
            1,
            [ValidationError("1 is not one of [0]")],
        ),
        (
            "format default message",
            {"format": "date-time"},
            "bla",
            [
                ValidationError(
                    "'bla' is not a 'date-time'",
                )
            ],
        ),
        (
            "a false schema",
            False,
            "foo",
            [ValidationError("False schema does not allow 'foo'")],
        ),
        (
            "valid if",
            {"if": {"type": "string"}, "then": True, "else": False},
            "",
            [],
        ),
        (
            "if then with false",
            {"if": {"type": "string"}, "then": False, "else": True},
            "a",
            [
                ValidationError(
                    "False schema does not allow 'a'",
                )
            ],
        ),
        (
            "valid else",
            {"if": {"type": "string"}, "then": False, "else": True},
            [],
            [],
        ),
        (
            "if then else with false",
            {"if": {"type": "string"}, "then": True, "else": False},
            [],
            [
                ValidationError(
                    "False schema does not allow []",
                )
            ],
        ),
        (
            "valid items",
            {"items": {"type": "string"}},
            ["foo"],
            [],
        ),
        (
            "valid items with wrong type",
            {"items": {"type": "string"}},
            {},
            [],
        ),
        (
            "items object",
            {"items": {"type": "string"}},
            [[]],
            [
                ValidationError(
                    "[] is not of type 'string'",
                )
            ],
        ),
        (
            "items list",
            {"items": [{"type": "string"}]},
            [[]],
            [
                ValidationError(
                    "[] is not of type 'string'",
                )
            ],
        ),
        (
            "valid multipleOf",
            {"multipleOf": 2},
            2,
            [],
        ),
        (
            "valid multipleOf with string",
            {"multipleOf": 2},
            "2",
            [],
        ),
        (
            "valid multipleOf with wrong type",
            {"multipleOf": 2},
            [],
            [],
        ),
        (
            "valid multipleOf with wrong type string",
            {"multipleOf": 2},
            "A",
            [],
        ),
        (
            "multipleOf",
            {"multipleOf": 2},
            3,
            [
                ValidationError(
                    "3 is not a multiple of 2",
                )
            ],
        ),
        (
            "multipleOf with string",
            {"multipleOf": 2},
            "3",
            [
                ValidationError(
                    "'3' is not a multiple of 2",
                )
            ],
        ),
        (
            "multipleOf with number",
            {"multipleOf": 2.0},
            "3",
            [
                ValidationError(
                    "'3' is not a multiple of 2.0",
                )
            ],
        ),
        (
            "valid minItems",
            {"minItems": 1},
            ["foo"],
            [],
        ),
        (
            "valid minItems with wrong type",
            {"minItems": 1},
            {},
            [],
        ),
        (
            "minItems",
            {"minItems": 2},
            [],
            [
                ValidationError(
                    "[] is too short (2)",
                )
            ],
        ),
        (
            "valid maxItems",
            {"maxItems": 1},
            ["foo"],
            [],
        ),
        (
            "valid maxItems with wrong type",
            {"maxItems": 1},
            {},
            [],
        ),
        (
            "maxItems",
            {"maxItems": 0},
            ["foo"],
            [
                ValidationError(
                    "['foo'] is too long (0)",
                )
            ],
        ),
        (
            "valid minLength",
            {"minLength": 1},
            "foo",
            [],
        ),
        (
            "valid minLength with wrong type",
            {"minLength": 1},
            1,
            [],
        ),
        (
            "minLength",
            {"minLength": 2},
            "",
            [
                ValidationError(
                    "'' is shorter than 2",
                )
            ],
        ),
        (
            "valid maxLength",
            {"maxLength": 3},
            "foo",
            [],
        ),
        (
            "valid maxLength with wrong type",
            {"maxLength": 1},
            1,
            [],
        ),
        (
            "maxLength",
            {"maxLength": 0},
            "foo",
            [
                ValidationError(
                    "'foo' is longer than 0",
                )
            ],
        ),
        (
            "valid not",
            {"not": False},
            True,
            [],
        ),
        (
            "not",
            {"not": True},
            False,
            [
                ValidationError(
                    "False should not be valid under True",
                )
            ],
        ),
        (
            "valid pattern",
            {"pattern": "^foo$"},
            "foo",
            [],
        ),
        (
            "valid pattern with wrong type",
            {"pattern": "^foo$"},
            {},
            [],
        ),
        (
            "pattern",
            {"pattern": "^a*$"},
            "bbb",
            [
                ValidationError(
                    "'bbb' does not match '^a*$'",
                )
            ],
        ),
        (
            "valid contains",
            {"contains": {"type": "string"}},
            ["foo"],
            [],
        ),
        (
            "valid contains with wrong type",
            {"contains": {"type": "string"}},
            {},
            [],
        ),
        (
            "contains",
            {"contains": {"type": "string"}},
            [],
            [
                ValidationError(
                    "[] does not contain items matching the given schema",
                )
            ],
        ),
        (
            "valid exclusiveMinimum",
            {"exclusiveMinimum": 4},
            5,
            [],
        ),
        (
            "valid exclusiveMinimum with wrong type",
            {"exclusiveMinimum": 4},
            {},
            [],
        ),
        (
            "valid exclusiveMinimum with non number string",
            {"exclusiveMinimum": 4},
            "foo",
            [],
        ),
        (
            "exclusiveMinimum",
            {"exclusiveMinimum": 5},
            5,
            [
                ValidationError(
                    "5 is less than or equal to the minimum of 5",
                )
            ],
        ),
        (
            "exclusiveMinimum with string",
            {"exclusiveMinimum": 5},
            "5",
            [
                ValidationError(
                    "'5' is less than or equal to the minimum of 5",
                )
            ],
        ),
        (
            "valid exclusiveMaximum",
            {"exclusiveMaximum": 5},
            4,
            [],
        ),
        (
            "valid exclusiveMaximum with wrong type",
            {"exclusiveMaximum": 5},
            {},
            [],
        ),
        (
            "valid exclusiveMaximum with wrong string type",
            {"exclusiveMaximum": 5},
            "foo",
            [],
        ),
        (
            "exclusiveMaximum with string",
            {"exclusiveMaximum": 5},
            "5",
            [
                ValidationError(
                    "'5' is greater than or equal to the maximum of 5",
                )
            ],
        ),
        (
            "valid required",
            {"required": ["foo"]},
            {"foo": False},
            [],
        ),
        (
            "valid required wrong type",
            {"required": ["foo"]},
            [],
            [],
        ),
        (
            "required",
            {"required": ["foo"]},
            {},
            [
                ValidationError(
                    "'foo' is a required property",
                )
            ],
        ),
        (
            "valid minProperties",
            {"minProperties": 1},
            {"foo": False},
            [],
        ),
        (
            "valid minProperties with wrong type",
            {"minProperties": 1},
            [],
            [],
        ),
        (
            "minProperties",
            {"minProperties": 1},
            {},
            [
                ValidationError(
                    "{} does not have enough properties",
                )
            ],
        ),
        (
            "valid maxProperties",
            {"maxProperties": 1},
            {"foo": False},
            [],
        ),
        (
            "valid maxProperties with wrong type",
            {"maxProperties": 1},
            [],
            [],
        ),
        (
            "maxProperties",
            {"maxProperties": 1},
            {"foo": {}, "bar": {}},
            [
                ValidationError(
                    "{'foo': {}, 'bar': {}} has too many properties",
                )
            ],
        ),
        (
            "valid patternProperties",
            {"patternProperties": {"^foo$": True}},
            {"foo": {}},
            [],
        ),
        (
            "valid patternProperties with wrong type",
            {"patternProperties": {"^foo$": True}},
            [],
            [],
        ),
        (
            "patternProperties",
            {"patternProperties": {"^foo$": False}},
            {"foo": "bar"},
            [
                ValidationError(
                    "False schema does not allow 'bar'",
                )
            ],
        ),
        (
            "valid properties",
            {"properties": {"foo": True}},
            {"foo": "bar"},
            [],
        ),
        (
            "valid properties with wrong type",
            {"properties": {"foo": True}},
            [],
            [],
        ),
        (
            "properties",
            {"properties": {"foo": False}},
            {"foo": "bar"},
            [
                ValidationError(
                    "False schema does not allow 'bar'",
                )
            ],
        ),
        (
            "valid propertyNames",
            {"propertyNames": {"pattern": "^bar$"}},
            {"bar": "foo"},
            [],
        ),
        (
            "valid propertyNames with wrong type",
            {"propertyNames": {"pattern": "^bar$"}},
            [],
            [],
        ),
        (
            "propertyNames",
            {"propertyNames": {"pattern": "^bar$"}},
            {"foo": "bar"},
            [
                ValidationError(
                    "'foo' does not match '^bar$'",
                )
            ],
        ),
        (
            "valid oneOf matches none",
            {"oneOf": [True]},
            False,
            [],
        ),
        (
            "oneOf matches none",
            {"oneOf": [False]},
            {},
            [
                ValidationError(
                    "{} is not valid under any of the given schemas",
                )
            ],
        ),
        (
            "oneOf matches too many",
            {"oneOf": [True, True]},
            {},
            [
                ValidationError(
                    "{} is valid under each of True, True",
                )
            ],
        ),
        (
            "valid allOf",
            {"allOf": [True, True]},
            False,
            [],
        ),
        (
            "allOf matches one False",
            {"allOf": [True, False]},
            {},
            [
                ValidationError(
                    "False schema does not allow {}",
                )
            ],
        ),
        (
            "allOf matches multiple False",
            {"allOf": [True, False, False]},
            {},
            [
                ValidationError(
                    "False schema does not allow {}",
                ),
                ValidationError(
                    "False schema does not allow {}",
                ),
            ],
        ),
        (
            "valid anyOf matches more than one",
            {"anyOf": [True, True]},
            False,
            [],
        ),
        (
            "anyOf matches none",
            {"anyOf": [False, False]},
            {},
            [
                ValidationError(
                    "{} is not valid under any of the given schemas",
                )
            ],
        ),
        (
            "valid uniqueItems",
            {"uniqueItems": True},
            [1, 2, "3"],
            [],
        ),
        (
            "uniqueItems",
            {"uniqueItems": True},
            [1, 2, "1"],
            [
                ValidationError(
                    "[1, 2, '1'] has non-unique elements",
                )
            ],
        ),
        (
            "valid requiredOr",
            {"requiredOr": ["foo", "bar"]},
            {"foo": {}},
            [],
        ),
        (
            "valid requiredOr with wrong type",
            {"requiredOr": ["foo", "bar"]},
            [],
            [],
        ),
        (
            "invalid requiredOr with empty object",
            {"requiredOr": ["foo", "bar"]},
            {},
            [
                ValidationError(
                    "One of ['foo', 'bar'] is a required property",
                )
            ],
        ),
        (
            "valid requiredXor",
            {"requiredXor": ["foo", "bar"]},
            {"foo": {}},
            [],
        ),
        (
            "valid requiredXor with wrong type",
            {"requiredXor": ["foo", "bar"]},
            [],
            [],
        ),
        (
            "requiredXor",
            {"requiredXor": ["foo", "bar"]},
            {},
            [
                ValidationError(
                    "Only one of ['foo', 'bar'] is a required property",
                )
            ],
        ),
        (
            "requiredXor with multiple errors",
            {"requiredXor": ["foo", "bar"]},
            {"foo": "foo", "bar": "bar"},
            [
                ValidationError(
                    "Only one of ['foo', 'bar'] is a required property",
                ),
                ValidationError(
                    "Only one of ['foo', 'bar'] is a required property",
                ),
            ],
        ),
        (
            "valid uniqueKeys",
            {"uniqueKeys": ["Name"]},
            [{"Name": "foo"}, {"Name": "bar"}],
            [],
        ),
        (
            "valid uniqueKeys with wrong types",
            {"uniqueKeys": ["Name"]},
            {"Name": "foo"},
            [],
        ),
        (
            "valid uniqueKeys with wrong type in array",
            {"uniqueKeys": ["Name"]},
            [{"Name": "foo"}, []],
            [],
        ),
        (
            "uniqueKeys",
            {"uniqueKeys": ["Name"]},
            [
                {
                    "Name": "foo",
                },
                {
                    "Name": "foo",
                },
            ],
            [
                ValidationError(
                    "[{'Name': 'foo'}, {'Name': 'foo'}] has non-unique "
                    "elements for keys ['Name']",
                )
            ],
        ),
        (
            "valid dependentExcluded when wrong type",
            {"dependentExcluded": {"foo": ["bar"]}},
            [],
            [],
        ),
        (
            "valid dependentExcluded when not specified",
            {"dependentExcluded": {"foo": ["bar"]}},
            {"bar": "bar"},
            [],
        ),
        (
            "dependentExcluded",
            {"dependentExcluded": {"foo": ["bar"], "bar": ["foo"]}},
            {"foo": "foo", "bar": "bar"},
            [
                ValidationError("'bar' should not be included with 'foo'"),
                ValidationError("'foo' should not be included with 'bar'"),
            ],
        ),
        (
            "dependentRequired",
            {"dependentRequired": {"foo": ["bar"]}},
            {"foo": "foo"},
            [
                ValidationError("'bar' is a dependency of 'foo'"),
            ],
        ),
        (
            "dependentRequired with multiple properties",
            {"dependentRequired": {"foo": ["a", "b"]}},
            {"foo": "foo"},
            [
                ValidationError("'a' is a dependency of 'foo'"),
                ValidationError("'b' is a dependency of 'foo'"),
            ],
        ),
        (
            "valid dependentRequired when property not included",
            {"dependentRequired": {"foo": ["a", "b"]}},
            {"bar": "bar"},
            [],
        ),
        (
            "valid dependentRequired",
            {"dependentRequired": {"foo": ["bar"]}},
            {"foo": "foo", "bar": "bar"},
            [],
        ),
        (
            "valid dependentRequired with wrong type",
            {"dependentRequired": {"foo": ["bar"]}},
            [],
            [],
        ),
        (
            "valid prefixItems",
            {"prefixItems": [{"type": "string"}]},
            ["foo"],
            [],
        ),
        (
            "invalid prefixItems with wrong type",
            {"prefixItems": [{"type": "string"}]},
            [1],
            [
                ValidationError("1 is not of type 'string'"),
            ],
        ),
    ],
)
@patch.object(ValidationError, "__eq__", spec=True, new=_eq)
@patch.object(ValidationError, "__lt__", spec=True, new=_lt)
def test_messages(name, schema, instance, expected, validator):
    validator = validator.evolve(schema=schema)
    errs = list(validator.iter_errors(instance))
    assert sorted(errs) == sorted(expected), f"{name!r} returned {errs!r}"
