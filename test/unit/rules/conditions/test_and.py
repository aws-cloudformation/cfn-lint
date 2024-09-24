"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.conditions.And import And


@pytest.fixture
def rule():
    rule = And()
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
            "Valid and with other conditions",
            {"Fn::And": [{"Condition": "IsUsEast1"}, {"Condition": "IsProduction"}]},
            {},
            [],
        ),
        (
            "Valid and with boolean types",
            {"Fn::And": [True, False]},
            {},
            [],
        ),
        (
            "Invalid Type",
            {"Fn::And": {}},
            {},
            [
                ValidationError(
                    "{} is not of type 'array'",
                    validator="fn_and",
                    schema_path=deque(["type"]),
                    path=deque(["Fn::And"]),
                ),
            ],
        ),
        (
            "Integer type",
            {"Fn::And": ["a", True]},
            {},
            [
                ValidationError(
                    "'a' is not of type 'boolean'",
                    validator="fn_and",
                    schema_path=deque(["fn_items", "type"]),
                    path=deque(["Fn::And", 0]),
                )
            ],
        ),
        (
            "Invalid functions in Conditions",
            {"Fn::And": [True, {"Fn::Contains": []}]},
            {"path": deque(["Conditions", "Condition1"])},
            [
                ValidationError(
                    "{'Fn::Contains': []} is not of type 'boolean'",
                    validator="fn_and",
                    schema_path=deque(["fn_items", "type"]),
                    path=deque(["Fn::And", 1]),
                )
            ],
        ),
        (
            "Valid functions in Rules",
            {"Fn::And": [True, {"Fn::Contains": []}]},
            {"path": deque(["Rules", "Rule1"])},
            [],
        ),
    ],
    indirect=["path"],
)
def test_condition(name, instance, errors, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == errors, name
