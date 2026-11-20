"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.conditions.Not import Not
from cfnlint.rules.conditions.Or import Or


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
            "Invalid literal boolean operand",
            {"Fn::Not": [True]},
            {},
            [
                ValidationError(
                    "True is not a valid Fn::Not operand; operands must "
                    "be a condition or a condition function",
                    validator="fn_not",
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "items",
                            "else",
                            "cfnContext",
                            "schema",
                            "not",
                        ]
                    ),
                    path=deque(["Fn::Not", 0]),
                ),
            ],
        ),
        (
            "Invalid boolean-like string operand",
            {"Fn::Not": ["false"]},
            {},
            [
                ValidationError(
                    "'false' is not a valid Fn::Not operand; operands must "
                    "be a condition or a condition function",
                    validator="fn_not",
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "items",
                            "else",
                            "cfnContext",
                            "schema",
                            "not",
                        ]
                    ),
                    path=deque(["Fn::Not", 0]),
                ),
            ],
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
            "Fn::GetAtt operand",
            {"Fn::Not": [{"Fn::GetAtt": ["MyBucket", "Arn"]}]},
            {},
            [
                ValidationError(
                    "{'Fn::GetAtt': ['MyBucket', 'Arn']} is not of type 'boolean'",
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


def test_literal_nested_in_or(rule, cfn, context):
    # The nested Fn::Or is only validated when its rule is registered
    # on the validator, as it is in a full template run.
    validator = CfnTemplateValidator({}).extend(validators={"fn_or": Or().fn_or})(
        context=context, cfn=cfn, schema={}
    )
    errs = list(
        rule.validate(
            validator,
            {},
            {"Fn::Not": [{"Fn::Or": [{"Condition": "IsUsEast1"}, True]}]},
            {},
        )
    )
    assert errs == [
        ValidationError(
            "True is not a valid Fn::Not operand; operands must "
            "be a condition or a condition function",
            validator="fn_not",
            schema_path=deque(
                [
                    "cfnContext",
                    "schema",
                    "items",
                    "else",
                    "cfnContext",
                    "schema",
                    "fn_or",
                    "cfnContext",
                    "schema",
                    "items",
                    "else",
                    "cfnContext",
                    "schema",
                    "not",
                ]
            ),
            path=deque(["Fn::Not", 0, "Fn::Or", 1]),
        )
    ]
