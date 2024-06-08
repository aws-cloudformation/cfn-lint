"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ServerlessTransform import ServerlessTransform


@pytest.fixture(scope="module")
def rule():
    rule = ServerlessTransform()
    yield rule


@pytest.mark.parametrize(
    "name,instance,template,expected",
    [
        (
            "Valid with transform",
            "AWS::Serverless::Function",
            {
                "Transform": ["AWS::Serverless-2016-10-31"],
            },
            [],
        ),
        (
            "Invalid type",
            [],
            {},
            [],
        ),
        (
            "Valid type without transform",
            "AWS::Lambda::Function",
            {},
            [],
        ),
        (
            "Invalid when not specified",
            "AWS::Serverless::Function",
            {},
            [
                ValidationError(
                    (
                        "'AWS::Serverless::Function' type used "
                        "without the serverless transform "
                        "'AWS::Serverless-2016-10-31'"
                    ),
                    rule=ServerlessTransform(),
                )
            ],
        ),
    ],
    indirect=["template"],
)
def test_validate(name, instance, template, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    assert errors == expected, f"Test {name!r} got {errors!r}"
