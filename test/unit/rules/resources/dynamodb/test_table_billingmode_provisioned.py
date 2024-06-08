"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.dynamodb.TableBillingModeProvisioned import (
    TableBillingModeProvisioned,
)


@pytest.fixture(scope="module")
def rule():
    rule = TableBillingModeProvisioned()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "BillingMode": "PAY_PER_REQUEST",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "BillingMode": "PROVISIONED",
                "ProvisionedThroughput": {
                    "WriteCapacityUnits": 5,
                    "ReadCapacityUnits": 5,
                },
            },
            [],
        ),
        (
            {
                "BillingMode": "PROVISIONED",
            },
            [
                ValidationError(
                    "'ProvisionedThroughput' is a required property",
                    rule=TableBillingModeProvisioned(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
