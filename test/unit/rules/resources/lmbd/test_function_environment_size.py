"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionEnvironmentSize import FunctionEnvironmentSize


@pytest.fixture(scope="module")
def rule():
    rule = FunctionEnvironmentSize()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"FOO": "bar"},
            [],
        ),
        (
            {},
            [],
        ),
        (
            # 4096 bytes of key and value, but 4103 as compact JSON
            {"A" * 2048: "B" * 2048},
            [
                ValidationError(
                    "Lambda environment variables total size (4103) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            {"A" * 2048: "B" * 2049},
            [
                ValidationError(
                    "Lambda environment variables total size (4104) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            # Exactly 4096 bytes as compact JSON stays silent
            {"K" * 2044: "V" * 2045},
            [],
        ),
        (
            # One byte over the limit as compact JSON
            {"K" * 2044: "V" * 2046},
            [
                ValidationError(
                    "Lambda environment variables total size (4097) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            # 100 variables: 3500 bytes of key and value, 4101 as
            # compact JSON (the 6n + 1 structural overhead matters)
            {f"V{i:03d}": "a" * 31 for i in range(100)},
            [
                ValidationError(
                    "Lambda environment variables total size (4101) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            {f"KEY{i}": "x" * 100 for i in range(50)},
            [
                ValidationError(
                    "Lambda environment variables total size (5541) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            # Non-ASCII values count as UTF-8 bytes, not escape sequences
            {"K": "é"},
            [],
        ),
        (
            # JSON escaping (quotes) counts toward the limit
            {"K": 'a"b'},
            [],
        ),
        (
            "not-an-object",
            [],
        ),
        (
            {"KEY": 12345},
            [],
        ),
        (
            {"KEY": ["a", "b"]},
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
