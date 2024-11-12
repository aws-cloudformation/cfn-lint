"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.elasticache.CacheClusterEngine import CacheClusterEngine


@pytest.fixture(scope="module")
def rule():
    rule = CacheClusterEngine()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Engine": "redis", "EngineVersion": 7.1},
            [],
        ),
        (
            {
                "Engine": "redis",
            },
            [],
        ),
        (
            {},
            [],
        ),
        (
            {
                "Engine": "redis",
                "EngineVersion": "7.1.0",
            },
            [
                ValidationError(
                    (
                        "'7.1.0' is not one of "
                        "['4.0.10', '5.0.6', "
                        "'6.0', '6.2', '7.0', '7.1']"
                    ),
                    validator="enum",
                    path=deque(["EngineVersion"]),
                    schema_path=[
                        "allOf",
                        2,
                        "then",
                        "properties",
                        "EngineVersion",
                        "enum",
                    ],
                    rule=CacheClusterEngine(),
                )
            ],
        ),
        (
            {
                "Engine": "oss-redis",
                "EngineVersion": "7.1",
            },
            [
                ValidationError(
                    ("'oss-redis' is not one of " "['memcached', 'redis', 'valkey']"),
                    validator="enum",
                    path=deque(["Engine"]),
                    schema_path=["allOf", 0, "then", "properties", "Engine", "enum"],
                    rule=CacheClusterEngine(),
                )
            ],
        ),
        (
            {
                "Engine": "redis",
                "EngineVersion": {"Ref": "AWS::AccountId"},
            },
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
