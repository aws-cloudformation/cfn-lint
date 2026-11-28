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
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsStaticFalse": {"Fn::Equals": ["false", "true"]},
            # Env can only be prod, so this comparison can never be true
            # (issue #5075).
            "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
        },
        "Parameters": {
            "MyParameter": {
                "Type": "String",
                "Default": "foobar",
            },
            "Env": {
                "Type": "String",
                "Default": "prod",
                "AllowedValues": ["prod"],
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
                    "{'Ref': 'MyParameter'} is not one of "
                    "['IsUsEast1', 'IsStaticFalse', 'IsDev']",
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
                    "'foo' is not one of ['IsUsEast1', 'IsStaticFalse', 'IsDev']",
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
                # The unreachable branch is not validated: CloudFormation
                # never passes its value to the resource (issue #5075).
            ],
        ),
        (
            # The true branch can never be chosen: IsStaticFalse is a
            # constant Fn::Equals of two unequal literals. Only W1028
            # reports the dead branch; the invalid value inside it is
            # not validated (issue #5074).
            "Dead true branch of an always-false condition is not validated",
            {"Fn::If": ["IsStaticFalse", "foo", True]},
            {"type": "boolean"},
            [
                ValidationError(
                    "['Fn::If', 1] is not reachable. When setting condition "
                    "'IsStaticFalse' to True",
                    path=deque(["Fn::If", 1]),
                ),
            ],
        ),
        (
            # The true branch can never be chosen: Env can only be prod,
            # so IsDev compares it against a value outside AllowedValues.
            # Only W1028 reports the dead branch (issue #5075).
            "Dead true branch outside AllowedValues is not validated",
            {"Fn::If": ["IsDev", "foo", True]},
            {"type": "boolean"},
            [
                ValidationError(
                    "['Fn::If', 1] is not reachable. When setting condition "
                    "'IsDev' to True",
                    path=deque(["Fn::If", 1]),
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
