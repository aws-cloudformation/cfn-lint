"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.properties.Tagging import Tagging


@pytest.fixture(scope="module")
def rule():
    rule = Tagging()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid tag by array",
            {"Tags": [{"Key": "Foo", "Value": "Bar"}]},
            {"taggable": True},
            [],
        ),
        (
            "Valid tag by key/value",
            {"Tags": {"Foo": "Bar"}},
            {"taggable": True},
            [],
        ),
        (
            "Duplicate key",
            {"Tags": [{"Key": "Foo", "Value": "Bar"}, {"Key": "Foo", "Value": "Bar"}]},
            {"taggable": True},
            [
                ValidationError(
                    (
                        "[{'Key': 'Foo', 'Value': 'Bar'}, "
                        "{'Key': 'Foo', 'Value': 'Bar'}] "
                        "has non-unique elements for keys ['Key']"
                    ),
                    path=deque(["Tags"]),
                    schema_path=deque(["properties", "Tags", "uniqueKeys"]),
                    validator="tagging",
                )
            ],
        ),
        (
            "Value is too long",
            {
                "Tags": [
                    {"Key": "Foo", "Value": "a" * 257},
                ]
            },
            {"taggable": True},
            [
                ValidationError(
                    f"{'a'*257!r} is longer than 256",
                    path=deque(["Tags", 0, "Value"]),
                    schema_path=deque(
                        [
                            "properties",
                            "Tags",
                            "items",
                            "properties",
                            "Value",
                            "maxLength",
                        ]
                    ),
                    validator="tagging",
                ),
            ],
        ),
        (
            "Value is too long in object",
            {
                "Tags": {"Foo": "a" * 257},
            },
            {"taggable": True},
            [
                ValidationError(
                    f"{'a'*257!r} is longer than 256",
                    path=deque(["Tags", "Foo"]),
                    schema_path=deque(
                        [
                            "properties",
                            "Tags",
                            "patternProperties",
                            "^(?!aws:).+$",
                            "maxLength",
                        ]
                    ),
                    validator="tagging",
                ),
            ],
        ),
        (
            "AWS key name in array",
            {
                "Tags": [
                    {"Key": "aws:Foo", "Value": "Bar"},
                ],
            },
            {"taggable": True},
            [
                ValidationError(
                    ("'aws:Foo' does not match " "'^(?!aws:).+$'"),
                    path=deque(["Tags", 0, "Key"]),
                    schema_path=deque(
                        ["properties", "Tags", "items", "properties", "Key", "pattern"]
                    ),
                    validator="tagging",
                ),
            ],
        ),
        (
            "AWS key name in object",
            {
                "Tags": {"aws:Foo": "Bar"},
            },
            {"taggable": True},
            [
                ValidationError(
                    (
                        "'aws:Foo' does not match any of "
                        "the regexes: "
                        "'^(?!aws:).+$'"
                    ),
                    path=deque(["Tags", "aws:Foo"]),
                    schema_path=deque(["properties", "Tags", "additionalProperties"]),
                    validator="tagging",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.tagging(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
