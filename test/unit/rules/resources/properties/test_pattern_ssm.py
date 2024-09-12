"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.parameters.ValuePattern import ValuePattern as ParameterPattern
from cfnlint.rules.resources.properties.Pattern import Pattern


@pytest.fixture(scope="module")
def rule():
    rule = Pattern()
    rule.child_rules["W2031"] = ParameterPattern()
    yield rule


@pytest.fixture
def template():
    return {
        "Transform": ["AWS::Serverless-2016-10-31"],
        "Parameters": {
            "SSMParameter": {
                "Type": "AWS::SSM::Parameter::Value<String>",
                "Default": "foo",
            },
            "Parameter": {
                "Type": "String",
                "Default": "bar",
            },
        },
    }


@pytest.mark.parametrize(
    "name,instance,pattern,expected",
    [
        (
            "Valid because SSM parameter default value",
            "foo",
            "bar",
            [],
        ),
        (
            "Invalid because not the SSM parameter",
            "bar",
            "foo",
            [
                ValidationError(
                    message="'bar' does not match 'foo'",
                )
            ],
        ),
        (
            "Invalid an unrelated to the parameters",
            "foobar",
            "foofoo",
            [
                ValidationError(
                    message="'foobar' does not match 'foofoo'",
                )
            ],
        ),
    ],
)
def test_validate(name, instance, pattern, expected, rule, validator):
    errs = list(rule.pattern(validator, pattern, instance, {}))
    assert errs == expected, f"{name} got errors {errs!r}"
