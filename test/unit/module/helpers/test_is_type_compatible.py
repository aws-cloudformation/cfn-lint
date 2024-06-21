"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.helpers import is_types_compatible


@pytest.mark.parametrize(
    "name,source,destination,expected",
    [
        (
            "Types are directly working together",
            "string",
            ["string"],
            True,
        ),
        (
            "Types can be converted from source to destiniation",
            "string",
            ["integer"],
            True,
        ),
        (
            "Types can be converted from destination to source",
            "integer",
            ["string"],
            True,
        ),
        (
            "Types of integer against array are not compatible",
            "integer",
            "array",
            False,
        ),
        (
            "Types of integer can be compatible",
            "integer",
            "number",
            True,
        ),
        (
            "Types of number are not an integer",
            "number",
            "integer",
            False,
        ),
        (
            "Types of integer is not compatible with boolean",
            "integer",
            "boolean",
            False,
        ),
        (
            "Types of number is not compatible with boolean",
            "number",
            "boolean",
            False,
        ),
        (
            "Types of number, string is compatible with boolean",
            ["number", "string"],
            "boolean",
            True,
        ),
    ],
)
def test_validate(name, source, destination, expected):
    result = is_types_compatible(source, destination)
    assert result == expected, f"Test {name!r} got {result!r}"
