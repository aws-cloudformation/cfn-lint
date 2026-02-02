"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.elasticache import (
    ReplicationGroupValkeyTransitEncryption as ValkeyRule,
)


@pytest.fixture(scope="module")
def rule():
    rule = ValkeyRule.ReplicationGroupValkeyTransitEncryption()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Engine": "valkey", "TransitEncryptionEnabled": True},
            [],
        ),
        (
            {"Engine": "valkey", "TransitEncryptionEnabled": False},
            [],
        ),
        (
            {"Engine": "redis", "TransitEncryptionEnabled": True},
            [],
        ),
        (
            {"Engine": "redis"},
            [],
        ),
        (
            {"Engine": "valkey"},
            [
                ValidationError(
                    "'TransitEncryptionEnabled' is a required property",
                    validator="required",
                    path=deque([]),
                    schema_path=deque(["then", "required"]),
                    rule=ValkeyRule.ReplicationGroupValkeyTransitEncryption(),
                )
            ],
        ),
        (
            {"Engine": {"Ref": "EngineParameter"}},
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
