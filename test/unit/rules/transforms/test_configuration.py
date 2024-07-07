"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.transforms.Configuration import Configuration


@pytest.fixture(scope="module")
def rule():
    rule = Configuration()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Empty list is ok",
            [],
            [],
        ),
        (
            "String is ok",
            "Foo",
            [],
        ),
        (
            "List is ok",
            ["Foo", "Bar"],
            [],
        ),
        (
            "Object is ok",
            {"Name": "Foo", "Parameters": {"Bar": "Test"}},
            [],
        ),
        (
            "Array of objects is ok",
            [
                {"Name": "Foo", "Parameters": {"Bar": "Test"}},
                "Foo",
            ],
            [],
        ),
        (
            "Missing required Name",
            {"Parameters": {"Bar": "Test"}},
            [
                ValidationError(
                    "'Name' is a required property",
                    validator="required",
                    rule=Configuration(),
                    path=deque([]),
                    schema_path=deque(["required"]),
                )
            ],
        ),
        (
            "No additional property names are allowed",
            {"Name": "Foo", "Foo": "Bar", "Parameters": {"Bar": "Test"}},
            [
                ValidationError(
                    "Additional properties are not allowed ('Foo' was unexpected)",
                    validator="additionalProperties",
                    rule=Configuration(),
                    path=deque(["Foo"]),
                    schema_path=deque(["additionalProperties"]),
                )
            ],
        ),
        (
            "Null is not ok",
            None,
            [
                ValidationError(
                    "None is not of type 'string', 'array', 'object'",
                    validator="type",
                    rule=Configuration(),
                    path=deque([]),
                    schema_path=deque(["type"]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
