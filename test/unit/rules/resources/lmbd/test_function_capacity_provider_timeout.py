"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.lmbd.FunctionCapacityProviderTimeout import (
    FunctionCapacityProviderTimeout,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionCapacityProviderTimeout()
    yield rule


_CAPACITY_PROVIDER_CONFIG = {
    "LambdaManagedInstancesCapacityProviderConfig": {
        "CapacityProviderArn": (
            "arn:aws:lambda:us-east-1:123456789012:capacity-provider:cp1"
        )
    }
}


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        # Valid: no Timeout at all
        (
            {"Runtime": "python3.13"},
            0,
            None,
        ),
        # Valid: classic function at the maximum
        (
            {"Timeout": 900},
            0,
            None,
        ),
        # Valid: classic function below the maximum
        (
            {"Timeout": 3},
            0,
            None,
        ),
        # Valid: LMI function above the classic maximum
        (
            {
                "Timeout": 5400,
                "CapacityProviderConfig": _CAPACITY_PROVIDER_CONFIG,
            },
            0,
            None,
        ),
        # Valid: LMI function at the classic maximum
        (
            {
                "Timeout": 900,
                "CapacityProviderConfig": _CAPACITY_PROVIDER_CONFIG,
            },
            0,
            None,
        ),
        # Valid: wrong type is handled elsewhere
        (
            [],
            0,
            None,
        ),
        # Invalid: classic function above the maximum
        (
            {"Timeout": 901},
            1,
            (
                "901 is greater than the maximum of 900 for functions "
                "without 'CapacityProviderConfig' (Lambda Managed Instances)"
            ),
        ),
        (
            {"Timeout": 5400},
            1,
            (
                "5400 is greater than the maximum of 900 for functions "
                "without 'CapacityProviderConfig' (Lambda Managed Instances)"
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
