"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionZipfileRuntimeEnum import (
    FunctionZipfileRuntimeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionZipfileRuntimeEnum()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Code": {"ZipFile": "foo"}, "Runtime": "python3.10"},
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {"Code": {"ZipFile": "foo"}, "Runtime": {"Ref": "Runtime"}},
            [],
        ),
        (
            {"Code": {"ZipFile": "foo"}, "Runtime": "bar"},
            [
                ValidationError(
                    "'bar' does not match '^(nodejs.*|python.*)$'",
                    rule=FunctionZipfileRuntimeEnum(),
                    path=deque(["Runtime"]),
                    validator="pattern",
                    schema_path=deque(["then", "properties", "Runtime", "pattern"]),
                )
            ],
        ),
        (
            {"Code": "../link/to/my/package.zip", "Runtime": "provided.al2023"},
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
