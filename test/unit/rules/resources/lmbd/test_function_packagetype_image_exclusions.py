"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.lmbd.FunctionPackageTypeImageExclusions import (
    FunctionPackageTypeImageExclusions,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionPackageTypeImageExclusions()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        # Valid cases - should not trigger rule
        (
            {
                "PackageType": "Zip",
                "Handler": "index.handler",
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
        # Invalid cases - should trigger rule
        (
            {
                "PackageType": "Image",
                "Handler": "index.handler",
            },
            1,
            (
                "Container image functions cannot specify "
                "Handler, Runtime, or Layers properties"
            ),
        ),
        (
            {
                "PackageType": "Image",
                "Runtime": "python3.14",
            },
            1,
            (
                "Container image functions cannot specify "
                "Handler, Runtime, or Layers properties"
            ),
        ),
        (
            {
                "PackageType": "Image",
                "Layers": ["arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1"],
            },
            1,
            (
                "Container image functions cannot specify "
                "Handler, Runtime, or Layers properties"
            ),
        ),
        (
            {
                "PackageType": "Image",
                "Handler": "index.handler",
                "Runtime": "python3.14",
                "Layers": ["arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1"],
            },
            1,
            (
                "Container image functions cannot specify "
                "Handler, Runtime, or Layers properties"
            ),
        ),
    ],
)
def test_validate(instance, expected_count, expected_message, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, (
        f"Expected {expected_count} errors got {len(errs)}"
    )
    if expected_message:
        assert errs[0].message == expected_message
