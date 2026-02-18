"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionPackageTypeLayers import (
    FunctionPackageTypeLayers,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionPackageTypeLayers()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        (
            {
                "PackageType": "Zip",
                "Layers": ["arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1"],
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
                "Layers": ["arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1"],
            },
            1,
            "False schema does not allow ['arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1']",
        ),
    ],
)
def test_validate(instance, expected_count, expected_message, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, f"Expected {expected_count} errors got {len(errs)}"
    if expected_message:
        assert errs[0].message == expected_message
