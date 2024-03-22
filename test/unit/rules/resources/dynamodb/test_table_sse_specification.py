"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.dynamodb.TableSseSpecification import TableSseSpecification


@pytest.fixture(scope="module")
def rule():
    rule = TableSseSpecification()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "KMSMasterKeyId": "",
                "SSEType": "KMS",
            },
            [],
        ),
        (
            {},  # nothing supplied
            [],
        ),
        (
            {
                "KMSMasterKeyId": "",
            },
            [
                ValidationError(
                    "'SSEType' is a dependency of 'KMSMasterKeyId'",
                    rule=TableSseSpecification(),
                    path=deque([]),
                    validator="dependentRequired",
                    schema_path=deque(["allOf", 0, "dependentRequired"]),
                )
            ],
        ),
        (
            {
                "KMSMasterKeyId": "",
                "SSEType": "FOO",
            },
            [
                ValidationError(
                    "'FOO' is not one of ['KMS']",
                    rule=TableSseSpecification(),
                    path=deque(["SSEType"]),
                    validator="enum",
                    schema_path=deque(["allOf", 1, "properties", "SSEType", "enum"]),
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
