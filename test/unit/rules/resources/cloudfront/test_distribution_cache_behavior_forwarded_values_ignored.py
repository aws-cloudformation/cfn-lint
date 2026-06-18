"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.cloudfront.DistributionCacheBehaviorForwardedValuesIgnored import (  # noqa: E501
    DistributionCacheBehaviorForwardedValuesIgnored,
)


@pytest.fixture(scope="module")
def rule():
    rule = DistributionCacheBehaviorForwardedValuesIgnored()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
                "ForwardedValues": {"QueryString": False},
            },
            [
                ValidationError(
                    "'ForwardedValues' is ignored when 'CachePolicyId' is specified",
                    path=deque(["ForwardedValues"]),
                ),
            ],
        ),
        (
            {
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
            },
            [],
        ),
        (
            {
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "none"},
                },
            },
            [],
        ),
        (
            {},
            [],
        ),
        (
            "not a dict",
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
