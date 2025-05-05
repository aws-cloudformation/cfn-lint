"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.conditions.Not import Not


@pytest.fixture
def rule():
    rule = Not()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {
            "Environment": {
                "Type": "String",
            }
        },
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsProduction": {"Fn::Equals": [{"Ref": "Environment"}, "Production"]},
        },
    }


@pytest.mark.parametrize(
    "name,instance,path,errors",
    [
        (
            "Valid or with other conditions",
            {"Fn::Not": [{"Condition": "IsUsEast1"}]},
            {},
            [],
        ),
        (
            "Valid or with boolean types",
            {"Fn::Not": [True]},
            {},
            [],
        ),
        (
            "Invalid Type",
            {"Fn::Not": {}},
            {},
            [
                ValidationError(
                    "{} is not of type 'array'",
                    validator="fn_not",
                    schema_path=deque(["cfnContext", "schema", "type"]),
                    path=deque(["Fn::Not"]),
                ),
            ],
        ),
        (
            "Integer type",
            {"Fn::Not": ["a"]},
            {},
            [
                ValidationError(
                    "'a' is not of type 'boolean'",
                    validator="fn_not",
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "items",
                            "else",
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    path=deque(["Fn::Not", 0]),
                )
            ],
        ),
        (
            "Invalid functions in Conditions",
            {"Fn::Not": [{"Fn::Contains": []}]},
            {"path": deque(["Conditions", "Condition1"])},
            [
                ValidationError(
                    "{'Fn::Contains': []} is not of type 'boolean'",
                    validator="fn_not",
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "items",
                            "else",
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    path=deque(["Fn::Not", 0]),
                )
            ],
        ),
        (
            "Valid functions in Rules",
            {"Fn::Not": [{"Fn::Contains": []}]},
            {"path": deque(["Rules", "Rule1"])},
            [],
        ),
    ],
    indirect=["path"],
)
def test_condition(name, instance, errors, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == errors, name
