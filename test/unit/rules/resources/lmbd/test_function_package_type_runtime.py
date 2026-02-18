"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionPackageTypeRuntime import (
    FunctionPackageTypeRuntime,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionPackageTypeRuntime()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        (
            {
                "PackageType": "Zip",
                "Runtime": "python3.14",
            },
            0,
            None,
        ),
        (
            {
                "PackageType": "Image",
            },
            0,
            None,
        ),
        (
            [],  # wrong type
            0,
            None,
        ),
        (
            {
                "PackageType": "Image",
                "Runtime": "python3.14",
            },
            1,
            "False schema does not allow 'python3.14'",
        ),
    ],
)
def test_validate(instance, expected_count, expected_message, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, f"Expected {expected_count} errors got {len(errs)}"
    if expected_message:
        assert errs[0].message == expected_message
