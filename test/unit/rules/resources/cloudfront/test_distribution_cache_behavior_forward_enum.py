"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.cloudfront.DistributionCacheBehaviorForwardEnum import (
    DistributionCacheBehaviorForwardEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = DistributionCacheBehaviorForwardEnum()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "none"},
                },
                "TargetOriginId": "myOrigin",
                "ViewerProtocolPolicy": "allow-all",
            },
            [],
        ),
        (
            {
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "all"},
                },
            },
            [],
        ),
        (
            {
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "whitelist"},
                },
            },
            [],
        ),
        (
            {
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "None"},
                },
            },
            [],
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
                    "Cookies": {"Forward": "None"},
                },
            },
            [
                ValidationError(
                    "'None' is not one of ['all', 'none', 'whitelist']",
                    rule=DistributionCacheBehaviorForwardEnum(),
                    path=deque(["ForwardedValues", "Cookies", "Forward"]),
                    schema_path=deque(
                        [
                            "else",
                            "properties",
                            "ForwardedValues",
                            "properties",
                            "Cookies",
                            "properties",
                            "Forward",
                            "enum",
                        ]
                    ),
                    validator="enum",
                ),
            ],
        ),
        (
            {
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "INVALID"},
                },
            },
            [
                ValidationError(
                    "'INVALID' is not one of ['all', 'none', 'whitelist']",
                    rule=DistributionCacheBehaviorForwardEnum(),
                    path=deque(["ForwardedValues", "Cookies", "Forward"]),
                    schema_path=deque(
                        [
                            "else",
                            "properties",
                            "ForwardedValues",
                            "properties",
                            "Cookies",
                            "properties",
                            "Forward",
                            "enum",
                        ]
                    ),
                    validator="enum",
                ),
            ],
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
