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
            {"A" * 2048: "B" * 2048},
            [],
        ),
        (
            {"A" * 2048: "B" * 2049},
            [
                ValidationError(
                    "Lambda environment variables total size (4097) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            {f"KEY{i}": "x" * 100 for i in range(50)},
            [
                ValidationError(
                    f"Lambda environment variables total size "
                    f"({sum(len(f'KEY{i}') + 100 for i in range(50))}) "
                    f"exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
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
