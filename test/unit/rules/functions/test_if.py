"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.If import If


@pytest.fixture(scope="module")
def rule():
    rule = If()
    yield rule


@pytest.fixture
def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
        },
        "Parameters": {
            "MyParameter": {
                "Type": "String",
                "Default": "foobar",
            },
        },
        "Resources": {},
    }


@pytest.fixture
def validator(cfn, context):
    validator = CfnTemplateValidator({}).extend(
        validators={
            "fn_if": If().fn_if,
        }
    )
    return validator(
        context=context,
        cfn=cfn,
        schema={},
    )


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::If",
            {"Fn::If": ["IsUsEast1", "foo", "bar"]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::If with to many arguments",
            {"Fn::If": ["IsUsEast1", "foo", "bar", "key"]},
            {"type": "string"},
            [
                ValidationError(
                    "expected maximum item count: 3, found: 4",
                    path=deque(["Fn::If"]),
                    schema_path=deque(["cfnContext", "schema", "maxItems"]),
                    validator="fn_if",
                ),
            ],
        ),
        (
            "Invalid Fn::If with bad first element",
            {"Fn::If": ["IsUsEast1", {"foo": "bar"}, "bar"]},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    path=deque(["Fn::If", 1]),
                    schema_path=deque(["type"]),
                    validator="type",
                ),
            ],
        ),
        (
            "Invalid Fn::If with bad condition",
            {"Fn::If": [{"Ref": "MyParameter"}, "foo", "bar"]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Ref': 'MyParameter'} is not one of ['IsUsEast1']",
                    path=deque(["Fn::If", 0]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            0,
                            "cfnContext",
                            "schema",
                            "dynamicValidation",
                            "enum",
                        ]
                    ),
                    validator="fn_if",
                ),
                ValidationError(
                    "{'Ref': 'MyParameter'} is not of type 'string'",
                    path=deque(["Fn::If", 0]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            0,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_if",
                ),
            ],
        ),
        (
            "Invalid Fn::If with bad second element",
            {"Fn::If": ["IsUsEast1", "foo", {"foo": "bar"}]},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    path=deque(["Fn::If", 2]),
                    schema_path=deque(["type"]),
                    validator="type",
                ),
            ],
        ),
        (
            "Invalid Fn::If a condition that doesn't exist",
            {"Fn::If": ["foo", True, False]},
            {"type": "boolean"},
            [
                ValidationError(
                    "'foo' is not one of ['IsUsEast1']",
                    path=deque(["Fn::If", 0]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            0,
                            "cfnContext",
                            "schema",
                            "dynamicValidation",
                            "enum",
                        ]
                    ),
                    validator="fn_if",
                ),
            ],
        ),
        (
            "Invalid path",
            {"Fn::If": ["IsUsEast1", True, {"Fn::If": ["IsUsEast1", "foo", False]}]},
            {"type": "boolean"},
            [
                ValidationError(
                    (
                        "['Fn::If', 1] is not reachable. When setting condition "
                        "'IsUsEast1' to True from current status False"
                    ),
                    path=deque(["Fn::If", 2, "Fn::If", 1]),
                    schema_path=deque(["fn_if"]),
                    validator="fn_if",
                ),
                ValidationError(
                    ("'foo' is not of type 'boolean'"),
                    path=deque(["Fn::If", 2, "Fn::If", 1]),
                    schema_path=deque(["fn_if", "type"]),
                    validator="type",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_if(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
