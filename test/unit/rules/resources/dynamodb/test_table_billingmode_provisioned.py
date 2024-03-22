"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.dynamodb.TableBillingModeProvisioned import (
    TableBillingModeProvisioned,
)


@pytest.fixture(scope="module")
def rule():
    rule = TableBillingModeProvisioned()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "BillingMode": "PROVISIONED",
                "ProvisionedThroughput": {},
            },
            [],
        ),
        (
            {},  # nothing supplied
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
    for err in errs:
        print(err.validator)
        print(err.path)
        print(err.schema_path)

    assert errs == expected, f"Expected {expected} got {errs}"
