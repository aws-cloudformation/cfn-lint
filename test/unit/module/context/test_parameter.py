"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter, _init_parameters


@pytest.mark.parametrize(
    "name,instance,expected_type,expected_ref",
    [
        ("Valid string parameter", {"Type": "string"}, "string", []),
        (
            "Valid parameter with default and allowed values",
            {
                "Type": "String",
                "Default": "foo",
                "AllowedValues": [
                    "foo",
                    "bar",
                ],
            },
            "String",
            [
                ("foo", deque(["AllowedValues", 0])),
                ("bar", deque(["AllowedValues", 1])),
            ],
        ),
        (
            "Valid parameter with a CommaDelimitedList",
            {
                "Type": "CommaDelimitedList",
                "Default": "foo",
            },
            "CommaDelimitedList",
            [
                (["foo"], deque(["Default"])),
            ],
        ),
        (
            "Valid parameter with a List of Numbers",
            {
                "Type": "List<Number>",
                "Default": "10,20",
            },
            "List<Number>",
            [(["10", "20"], deque(["Default"]))],
        ),
        (
            "Valid parameter with a List of numbers for allowed values",
            {
                "Type": "List<Number>",
                "AllowedValues": ["10,20"],
            },
            "List<Number>",
            [(["10", "20"], deque(["AllowedValues", 0]))],
        ),
        (
            "Valid parameter with a SSM Parameter",
            {
                "Type": "AWS::SSM::Parameter::Value<String>",
                "Default": "foo",
            },
            "AWS::SSM::Parameter::Value<String>",
            [],
        ),
        (
            "Valid parameter with a MinValue and MaxValue",
            {"Type": "Number", "MinValue": "10", "MaxValue": "20"},
            "Number",
            [("10", deque(["MinValue"])), ("20", deque(["MaxValue"]))],
        ),
        (
            "Valid list parameter with an integer value",
            {"Type": "List<Number>", "Default": 10},
            "List<Number>",
            [(["10"], deque(["Default"]))],
        ),
        (
            "Valid list parameter with an integer value",
            {"Type": "List<Number>", "AllowedValues": [10]},
            "List<Number>",
            [(["10"], deque(["AllowedValues", 0]))],
        ),
    ],
)
def test_parameter(name, instance, expected_type, expected_ref):
    context = Context(["us-east-1"])
    parameter = Parameter(instance)

    assert expected_type == parameter.type
    assert expected_ref == list(
        parameter.ref(context)
    ), f"{name!r} test got {list(parameter.ref(context))}"


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        ("Valid string parameter", {"Type": "string"}, False),
        (
            "Valid string parameter with no echo string",
            {"Type": "string", "NoEcho": "true"},
            True,
        ),
        (
            "Valid string parameter with no echo boolean",
            {"Type": "string", "NoEcho": True},
            True,
        ),
    ],
)
def test_no_echo(name, instance, expected):
    parameter = Parameter(instance)

    assert expected == parameter.no_echo, f"{name} failed got {parameter.no_echo}"


@pytest.mark.parametrize(
    "name,instance",
    [
        ("Invalid Type", {"Type": {}}),
    ],
)
def test_errors(name, instance):
    with pytest.raises(ValueError):
        Parameter(instance)


def test_parameters():
    with pytest.raises(ValueError):
        _init_parameters([])
