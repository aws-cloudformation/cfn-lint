"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.Cidr import Cidr


@pytest.fixture(scope="module")
def rule():
    rule = Cidr()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Cidr with 2 element array",
            {"Fn::Cidr": ["192.168.0.0/24", 6]},
            {"type": "array"},
            [],
        ),
        (
            "Valid Fn::Cidr with 3 element array",
            {"Fn::Cidr": ["192.168.0.0/24", 6, 5]},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Fn::Cidr with wrong output type",
            {"Fn::Cidr": ["192.168.0.0/24", 2]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::Cidr': ['192.168.0.0/24', 2]} is not of type 'string'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_cidr",
                ),
            ],
        ),
        (
            "Invalid Fn::Cidr is NOT a array",
            {"Fn::Cidr": "foo"},
            {"type": "array"},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Cidr"]),
                    schema_path=deque(["cfnContext", "schema", "type"]),
                    validator="fn_cidr",
                ),
            ],
        ),
        (
            "Valid Fn::Cidr with a valid function",
            {"Fn::Cidr": ["192.168.0.0/24", {"Fn::FindInMap": ["A", "B", "D"]}]},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Fn::Cidr with an invalid function",
            {"Fn::Cidr": ["192.168.0.0/24", {"Fn::Join": ["-", "bar"]}]},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::Join': ['-', 'bar']} is not of type 'integer'",
                    path=deque(["Fn::Cidr", 1]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            1,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_cidr",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_cidr(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
