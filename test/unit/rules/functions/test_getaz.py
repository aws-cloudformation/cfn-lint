"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.helpers import REGIONS
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.GetAz import GetAz


@pytest.fixture(scope="module")
def rule():
    rule = GetAz()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::GetAZs with empty string",
            {"Fn::GetAZs": ""},
            {"type": "array"},
            [],
        ),
        (
            "Valid Fn::GetAZs with Ref",
            {"Fn::GetAZs": {"Ref": "AWS::Region"}},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Fn::GetAZs with an invalid output type",
            {"Fn::GetAZs": {"Ref": "AWS::Region"}},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::GetAZs': {'Ref': 'AWS::Region'}} is not of type 'string'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_getazs",
                ),
            ],
        ),
        (
            "Invalid Fn::GetAZs with a bad value type",
            {"Fn::GetAZs": ["foo"]},
            {"type": "array"},
            [
                ValidationError(
                    "['foo'] is not of type 'string'",
                    path=deque(["Fn::GetAZs"]),
                    schema_path=deque(["type"]),
                    validator="fn_getazs",
                ),
                ValidationError(
                    f"['foo'] is not one of {[''] + REGIONS!r}",
                    path=deque(["Fn::GetAZs"]),
                    schema_path=deque(["enum"]),
                    validator="fn_getazs",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_getazs(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
