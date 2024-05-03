"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.jsonschema.CfnLint import CfnLint
from cfnlint.rules.resources.dynamodb.TableBillingModeExclusive import (
    TableBillingModeExclusive,
)
from cfnlint.rules.resources.properties.Properties import Properties as PropertyRule


@pytest.fixture(scope="module")
def rule():
    rule = PropertyRule()
    cfn_lint_rule = CfnLint()
    cfn_lint_rule.child_rules["E3638"] = TableBillingModeExclusive()
    rule.child_rules["E1101"] = cfn_lint_rule
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


@pytest.mark.parametrize(
    "properties,expected",
    [
        (
            {
                "BillingMode": "PAY_PER_REQUEST",
                "KeySchema": [
                    {
                        "AttributeName": "foo",
                        "KeyType": "HASH",
                    }
                ],
                "ProvisionedThroughput": {
                    "WriteCapacityUnits": 5,
                    "ReadCapacityUnits": 5,
                },
            },
            [
                ValidationError(
                    "Additional properties are not allowed ('ProvisionedThroughput'}",
                    rule=TableBillingModeExclusive(),
                    path=deque(["Properties", "ProvisionedThroughput"]),
                    validator=None,
                    schema_path=deque(
                        ["cfnLint", "then", "properties", "ProvisionedThroughput"]
                    ),
                )
            ],
        ),
        (
            {
                "BillingMode": "PAY_PER_REQUEST",
                "KeySchema": [
                    {
                        "AttributeName": "foo",
                        "KeyType": "HASH",
                    }
                ],
            },
            [],
        ),
        (
            {
                "BillingMode": "PROVISIONED",
                "KeySchema": [
                    {
                        "AttributeName": "foo",
                        "KeyType": "HASH",
                    }
                ],
                "ProvisionedThroughput": {
                    "WriteCapacityUnits": 5,
                    "ReadCapacityUnits": 5,
                },
            },
            [],
        ),
    ],
)
def test_validate(properties, expected, rule, validator):
    validator = validator.evolve(schema={})
    errs = list(
        rule.cfnresourceproperties(
            validator,
            None,
            {"Type": "AWS::DynamoDB::Table", "Properties": properties},
            {},
        )
    )

    assert errs == expected, f"Expected {expected} got {errs}"
