"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.formats._schema_comparer import compare_schemas


@pytest.mark.parametrize(
    "name,source,destination,expected",
    [
        (
            "basic valid",
            {"format": "foo"},
            {"format": "foo"},
            None,
        ),
        (
            "basic invalid",
            {"format": "foo"},
            {"format": "bar"},
            ValidationError(
                "'foo' format is incompatible with formats ['bar']",
            ),
        ),
        (
            "basic invalid with no destination",
            {"format": "foo"},
            {},
            ValidationError(
                "'foo' format is incompatible",
            ),
        ),
        (
            "backwards compatibility",
            {"format": "AWS::EC2::SecurityGroup.GroupId"},
            {"format": "AWS::EC2::SecurityGroup.Id"},
            None,
        ),
        (
            "basic valid with anyOf source",
            {"anyOf": [{"format": "foo"}, {"format": "bar"}]},
            {"format": "foo"},
            None,
        ),
        (
            "basic valid with anyOf source with no valid formats",
            {"anyOf": [{"format": "bar"}, {"format": "foobar"}]},
            {"format": "foo"},
            None,
        ),
        (
            "basic valid with anyOf destination",
            {"format": "foo"},
            {"anyOf": [{"format": "foo"}, {"format": "bar"}]},
            None,
        ),
        (
            "basic invalid with anyOf destination with many invalid",
            {"format": "foo"},
            {"anyOf": [{"format": "bar"}, {"format": "foobar"}]},
            ValidationError(
                "'foo' format is incompatible with formats ['bar', 'foobar']",
            ),
        ),
    ],
)
def test_schema_comparer(name, source, destination, expected):
    result = compare_schemas(source, destination)

    assert result == expected, f"{name!r} got errors {result!r}"
