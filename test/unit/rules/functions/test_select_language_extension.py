"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.Select import Select
from cfnlint.rules.functions.SelectResolved import SelectResolved


@pytest.fixture(scope="module")
def rule():
    rule = Select()
    rule.child_rules["W1035"] = SelectResolved()
    yield rule


@pytest.fixture
def template():
    return {"Transform": "AWS::LanguageExtensions"}


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Invalid Fn::Select using an invalid function for index",
            {"Fn::Select": [{"Fn::GetAtt": "MyResource"}, ["bar"]]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::GetAtt': 'MyResource'} is not of type 'integer'",
                    path=deque(["Fn::Select", 0]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_select",
                ),
            ],
        ),
        (
            "Valid Fn::Length with language extension",
            {"Fn::Select": [{"Fn::Length": [1, 2]}, ["A", "B", "C"]]},
            {"type": "string"},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_select(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
