"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.metadata.Configuration import Configuration


@pytest.fixture(scope="module")
def rule():
    rule = Configuration()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Metadata",
            {"Foo": "Bar"},
            [],
        ),
        (
            "Wrong type",
            [],
            [
                ValidationError(
                    ("[] is not of type 'object'"),
                    validator="type",
                    schema_path=deque(["type"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Invalid with a null",
            {"foo": None},
            [
                ValidationError(
                    (
                        "None is not of type "
                        "'string', 'integer', 'object', "
                        "'array', 'boolean'"
                    ),
                    validator="type",
                    schema_path=deque(["additionalProperties", "type"]),
                    path=deque(["foo"]),
                    rule=Configuration(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
