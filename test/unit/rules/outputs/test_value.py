"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.Cidr import Cidr
from cfnlint.rules.functions.Join import Join
from cfnlint.rules.functions.Ref import Ref
from cfnlint.rules.functions.RefResolved import RefResolved
from cfnlint.rules.outputs.Value import Value  # pylint: disable=E0401


@pytest.fixture
def template():
    return {
        "Parameters": {
            "additionalVpcCidr": {
                "Type": "String",
                "Default": "",
            },
            "badAdditionalVpcCidr": {
                "Type": "String",
                "Default": "1",
            },
        },
        "Conditions": {
            "isAdditionalVpc": {
                "Fn::Not": [
                    {
                        "Fn::Equals": [
                            {"Ref": "additionalVpcCidr"},
                            "",
                        ]
                    }
                ]
            },
            "isBadAdditionalVpc": {
                "Fn::Not": [
                    {
                        "Fn::Equals": [
                            {"Ref": "badAdditionalVpcCidr"},
                            "",
                        ]
                    }
                ]
            },
        },
    }


@pytest.fixture
def validator(cfn):

    ref = Ref()
    ref.child_rules["W1030"] = RefResolved()
    yield CfnTemplateValidator(schema={}).extend(
        validators={
            "fn_join": Join().fn_join,
            "ref": ref.ref,
            "fn_cidr": Cidr().fn_cidr,
        }
    )(
        schema={},
        cfn=cfn,
    )


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            {
                "Value": "foo",
            },
            [],
        ),
        (
            {
                "Value": 1.0,
            },
            [
                ValidationError(
                    "1.0 is not of type 'array', 'string'",
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque(["Value"]),
                    rule=Value(),
                )
            ],
        ),
        (
            {
                "Value": 1,
            },
            [
                ValidationError(
                    "1 is not of type 'array', 'string'",
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque(["Value"]),
                    rule=Value(),
                )
            ],
        ),
        (
            {"Value": True},
            [
                ValidationError(
                    "True is not of type 'array', 'string'",
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque(["Value"]),
                    rule=Value(),
                )
            ],
        ),
        (
            {"Value": [{}]},
            [
                ValidationError(
                    "{} is not of type 'string'",
                    validator="type",
                    schema_path=deque(["items", "type"]),
                    path=deque(["Value", 0]),
                    rule=Value(),
                )
            ],
        ),
        (
            {"Value": {"foo": "bar"}},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'array', 'string'",
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque(["Value"]),
                    rule=Value(),
                )
            ],
        ),
        (
            {
                "Condition": "isAdditionalVpc",
                "Value": {
                    "Fn::Join": [
                        ",",
                        {"Fn::Cidr": [{"Ref": "additionalVpcCidr"}, 3, 8]},
                    ]
                },
            },
            [],
        ),
        (
            {
                "Condition": "isBadAdditionalVpc",
                "Value": {
                    "Fn::Join": [
                        ",",
                        {"Fn::Cidr": [{"Ref": "badAdditionalVpcCidr"}, 3, 8]},
                    ]
                },
            },
            [
                ValidationError(
                    (
                        "{'Ref': 'badAdditionalVpcCidr'} does not match "
                        "'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\\\\/([0-9]|[1-2][0-9]|3[0-2]))$'"
                        " when 'Ref' is resolved"
                    ),
                    validator="ref",
                    schema_path=deque(
                        ["fn_join", "fn_items", "fn_cidr", "fn_items", "ref", "pattern"]
                    ),
                    path=deque(["Value", "Fn::Join", 1, "Fn::Cidr", 0, "Ref"]),
                    rule=RefResolved(),
                )
            ],
        ),
    ],
)
def test_output_value(input, expected, validator):
    rule = Value()
    results = list(rule.validate(validator, {}, input, {}))

    assert results == expected, f"Expected {expected} results, got {results}"
