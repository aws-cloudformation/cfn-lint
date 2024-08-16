"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.cloudfront.DistributionTargetOriginId import (
    DistributionTargetOriginId,
)


@pytest.fixture(scope="module")
def rule():
    rule = DistributionTargetOriginId()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            [],  # wrong type should return no issues
            [],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": "origin-id",
                },
                "Origins": [
                    {
                        "Id": "origin-id",
                    },
                ],
            },
            [],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": "origin-id",
                },
                "Origins": [
                    {
                        "Id": "foo",
                    },
                    {
                        "Id": "origin-id",
                    },
                    {
                        "Id": "bar",
                    },
                ],
            },
            [],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": "origin-id",
                },
                "Origins": [
                    {
                        "Id": "foo",
                    },
                    {
                        "Id": "bar",
                    },
                ],
            },
            [
                ValidationError(
                    ("'origin-id' is not one of ['foo', 'bar']"),
                    rule=DistributionTargetOriginId(),
                    path=deque([]),
                    validator="enum",
                    path_override=deque(["DefaultCacheBehavior", "TargetOriginId"]),
                )
            ],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": {"Ref": "MyParameter"},
                },
                "Origins": [
                    {
                        "Id": "foo",
                    },
                    {
                        "Id": "bar",
                    },
                ],
            },
            [],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": "origin-id",
                },
                "Origins": [
                    {
                        "Id": "foo",
                    },
                    {
                        "Id": {"Ref": "MyParameter"},
                    },
                    {
                        "Id": "bar",
                    },
                ],
            },
            [],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": "origin-id",
                },
                "Origins": [
                    {
                        "Id": "foo",
                    },
                    {
                        "Id": "bar",
                    },
                ],
                "OriginGroups": {
                    "Items": [
                        {
                            "Id": "group-1",
                        },
                        {
                            "Id": "group-2",
                        },
                    ]
                },
            },
            [
                ValidationError(
                    (
                        "'origin-id' is not one of "
                        "['foo', 'bar', 'group-1', 'group-2']"
                    ),
                    rule=DistributionTargetOriginId(),
                    path=deque([]),
                    validator="enum",
                    path_override=deque(["DefaultCacheBehavior", "TargetOriginId"]),
                )
            ],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": "origin-id",
                },
                "Origins": [
                    {
                        "Id": "foo",
                    },
                    {
                        "Id": "bar",
                    },
                ],
                "OriginGroups": {
                    "Items": [
                        {
                            "Id": "group-1",
                        },
                        {
                            "Id": "origin-id",
                        },
                    ]
                },
            },
            [],
        ),
        (
            {
                "DefaultCacheBehavior": {
                    "TargetOriginId": "origin-id",
                },
                "Origins": [
                    {
                        "Id": "foo",
                    },
                    {
                        "Id": "bar",
                    },
                ],
                "OriginGroups": {
                    "Items": [
                        {
                            "Id": "group-1",
                        },
                        {
                            "Id": {"Ref": "MyParameter"},
                        },
                    ]
                },
            },
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
