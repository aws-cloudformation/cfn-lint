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
                    "['Fn::If', 1] is not reachable. When setting condition "
                    "'IsUsEast1' to True from current status False",
                    path=deque(["Fn::If", 2, "Fn::If", 1]),
                    schema_path=deque(["fn_if"]),
                    validator="fn_if",
                ),
                ValidationError(
                    "'foo' is not of type 'boolean'",
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


@pytest.mark.parametrize(
    "name,assumed,expected",
    [
        (
            # The condition was pinned by condition-scenario enumeration
            # (assumed), e.g. a schema if/then.  The contradicting branch is
            # still reachable in its own scenario, so W1028 must not fire.
            # Regression test for issue #4673.
            "Condition pinned by scenario enumeration is not unreachable",
            True,
            [],
        ),
        (
            # The condition is a forced fact (e.g. a resource-level Condition
            # or an enclosing Fn::If), so the branch that contradicts it is
            # truly dead.
            "Condition pinned as a fact is unreachable",
            False,
            [
                ValidationError(
                    "['Fn::If', 1] is not reachable. When setting condition "
                    "'IsUsEast1' to True from current status False",
                    path=deque(["Fn::If", 1]),
                ),
            ],
        ),
    ],
)
def test_validate_pinned_condition(name, assumed, expected, rule, validator):
    # Pin IsUsEast1 to False, mirroring how the walk arrives at an Fn::If with
    # a condition already fixed.  When the pin is only assumed (enumeration)
    # the contradicting branch stays reachable; when it is a fact the branch is
    # unreachable.
    pinned_validator = validator.evolve(
        context=validator.context.evolve(
            conditions=validator.context.conditions.evolve(
                {"IsUsEast1": False}, assumed=assumed
            ),
        )
    )
    instance = {"Fn::If": ["IsUsEast1", "foo", "bar"]}
    errs = list(rule.fn_if(pinned_validator, {"type": "string"}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
