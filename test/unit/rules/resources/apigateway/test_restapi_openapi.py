"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.apigateway.RestApiOpenApi import RestApiOpenApi


@pytest.fixture(scope="module")
def rule():
    rule = RestApiOpenApi()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Name": "Foo",
            },
            [],
        ),
        (
            {
                "Body": "Foo",
            },
            [],
        ),
        (
            {
                "BodyS3Location": "s3://foo",
            },
            [],
        ),
        (
            {},
            [
                ValidationError(
                    (
                        "'Name' is a required property when not specifying "
                        "one of ['Body', 'BodyS3Location']"
                    ),
                    rule=RestApiOpenApi(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["else", "required"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
