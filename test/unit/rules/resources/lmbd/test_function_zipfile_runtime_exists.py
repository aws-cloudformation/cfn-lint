"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionZipfileRuntimeExists import (
    FunctionZipfileRuntimeExists,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionZipfileRuntimeExists()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Code": {
                    "ZipFile": "foo",
                },
                "Runtime": "foo",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "Code": {"ZipFile": "foo"},
            },
            [
                ValidationError(
                    "'Runtime' is a required property",
                    rule=FunctionZipfileRuntimeExists(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
