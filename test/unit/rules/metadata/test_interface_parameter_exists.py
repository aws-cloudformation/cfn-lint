"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.metadata.InterfaceParameterExists import InterfaceParameterExists


@pytest.fixture(scope="module")
def rule():
    rule = InterfaceParameterExists()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {
            "Foo": {"Type": "String"},
        },
    }


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Interface",
            "Foo",
            [],
        ),
        (
            "Wrong parameter",
            "Bar",
            [
                ValidationError(
                    ("'Bar' is not one of ['Foo']"),
                    validator="enum",
                    schema_path=deque(["enum"]),
                    rule=InterfaceParameterExists(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
