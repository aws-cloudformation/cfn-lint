"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.SubParametersUsed import SubParametersUsed


@pytest.fixture(scope="module")
def rule():
    rule = SubParametersUsed()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        ("Valid with matching parameters", ["${Foo}", {"Foo": "Bar"}], []),
        (
            "Invalid with a missing parameter",
            ["${Foo}", {"Foo": "Bar", "Bar": "Foo"}],
            [ValidationError("Parameter 'Bar' not used in 'Fn::Sub'", path=[1, "Bar"])],
        ),
    ],
)
def test_sub_parameters_used(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))
    assert errors == expected, f"Test {name!r} got {errors!r}"
