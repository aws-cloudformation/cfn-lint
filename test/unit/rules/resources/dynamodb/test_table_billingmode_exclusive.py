"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.dynamodb.TableBillingModeExclusive import (
    TableBillingModeExclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = TableBillingModeExclusive()
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
                "BillingMode": "PAY_PER_REQUEST",
                "ProvisionedThroughput": "FOO",
            },
            [
                ValidationError(
                    "Additional properties are not allowed ('ProvisionedThroughput')",
                    rule=TableBillingModeExclusive(),
                    path=deque(["ProvisionedThroughput"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "ProvisionedThroughput"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
