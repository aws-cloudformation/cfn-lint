"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter


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
    ],
)
def test_parameter(name, instance, expected_type, expected_ref):
    context = Context(["us-east-1"])
    parameter = Parameter(instance)

    assert expected_type == parameter.type
    assert expected_ref == list(parameter.ref(context))
