"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions._BaseFn import BaseFn


@pytest.fixture(scope="module")
def rule():
    rule = BaseFn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Dynamic references are ignored",
            {"Fn::Sub": "{{resolve:ssm:${AWS::AccountId}/${AWS::Region}/ac}}"},
            {"enum": ["Foo"]},
            [],
        ),
        ("Everything is fine", {"Fn::Sub": "Foo"}, {"enum": ["Foo"]}, []),
        (
            "Standard error",
            {"Fn::Sub": "Bar"},
            {"enum": ["Foo"]},
            [
                ValidationError(
                    message=(
                        "{'Fn::Sub': 'Bar'} is not one of "
                        "['Foo'] when '' is resolved"
                    ),
                    path=deque(["Fn::Sub"]),
                    validator="",
                    schema_path=deque(["enum"]),
                )
            ],
        ),
    ],
)
def test_resolve(name, instance, schema, expected, validator, rule):
    errs = list(rule.resolve(validator, schema, instance, {}))
    assert errs == expected, f"{name!r} failed and got errors {errs!r}"
