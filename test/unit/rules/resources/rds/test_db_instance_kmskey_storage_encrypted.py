"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceKmsKeyStorageEncrypted import (
    DbInstanceKmsKeyStorageEncrypted,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceKmsKeyStorageEncrypted()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Engine": "postgres",
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/1234",
                "StorageEncrypted": True,
            },
            [],
        ),
        (
            {
                "Engine": "postgres",
                "StorageEncrypted": True,
            },
            [],
        ),
        (
            {
                "Engine": "postgres",
            },
            [],
        ),
        (
            {
                "Engine": "custom-sqlserver-se",
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/1234",
            },
            [],
        ),
        (
            {
                "Engine": "custom-oracle-ee",
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/1234",
            },
            [],
        ),
        (
            {
                "Engine": "postgres",
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/1234",
            },
            [
                ValidationError(
                    "'StorageEncrypted' is a required property",
                    rule=DbInstanceKmsKeyStorageEncrypted(),
                    path=deque([]),
                    schema_path=deque(["then", "required"]),
                    validator="required",
                ),
            ],
        ),
        (
            {
                "Engine": "mysql",
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/1234",
            },
            [
                ValidationError(
                    "'StorageEncrypted' is a required property",
                    rule=DbInstanceKmsKeyStorageEncrypted(),
                    path=deque([]),
                    schema_path=deque(["then", "required"]),
                    validator="required",
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
