"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.mappings.Configuration import Configuration


@pytest.fixture(scope="module")
def rule():
    rule = Configuration()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Empty is okay",
            {"MyMapping": {"Key": {"Value": "Foo"}}},
            [],
        ),
        (
            "Good key name",
            {"MyMapping": {"Foo-Bar": {"Value": "Foo"}}},
            [],
        ),
        (
            "Wrong type",
            [],
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["type"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Bad mapping type",
            {"MyMapping": []},
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["patternProperties", "^[a-zA-Z0-9]+$", "type"]),
                    rule=Configuration(),
                    path=deque(["MyMapping"]),
                )
            ],
        ),
        (
            "Bad key type",
            {"MyMapping": {"Key": []}},
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "patternProperties",
                            "^[a-zA-Z0-9.-]+$",
                            "type",
                        ]
                    ),
                    rule=Configuration(),
                    path=deque(
                        [
                            "MyMapping",
                            "Key",
                        ]
                    ),
                )
            ],
        ),
        (
            "Bad value type",
            {"MyMapping": {"Key": {"Value": {}}}},
            [
                ValidationError(
                    (
                        "{} is not of type 'string', 'boolean', "
                        "'integer', 'number', 'array'"
                    ),
                    validator="type",
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "patternProperties",
                            "^[a-zA-Z0-9.-]+$",
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "type",
                        ]
                    ),
                    rule=Configuration(),
                    path=deque(["MyMapping", "Key", "Value"]),
                )
            ],
        ),
        (
            "Bad Name",
            {"MyMapping-1": {"Key": {"Value": "Foo"}}},
            [
                ValidationError(
                    "'MyMapping-1' does not match any of the regexes: '^[a-zA-Z0-9]+$'",
                    validator="additionalProperties",
                    schema_path=deque(["additionalProperties"]),
                    rule=Configuration(),
                    path=deque(["MyMapping-1"]),
                )
            ],
        ),
        (
            "Long key name",
            {"a" * 256: {"Key": {"Value": "Foo"}}},
            [
                ValidationError(
                    "expected maximum length: 255, found: 256",
                    validator="maxLength",
                    schema_path=deque(["propertyNames", "maxLength"]),
                    rule=None,  # empty because we didn't load child rules
                    path=deque(["a" * 256]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
