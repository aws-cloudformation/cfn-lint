"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.parameters.Types import Types


@pytest.fixture(scope="module")
def rule():
    rule = Types()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid String type",
            "String",
            [],
        ),
        (
            "Valid Number type",
            "Number",
            [],
        ),
        (
            "Valid AWS-specific type",
            "AWS::EC2::VPC::Id",
            [],
        ),
        (
            "Valid SSM parameter type",
            "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
            [],
        ),
        (
            "Valid List type",
            "List<AWS::EC2::Subnet::Id>",
            [],
        ),
        (
            "Unsupported but accepted SSM type",
            "AWS::SSM::Parameter::Value<AWS::EC2::PrefixList::Id>",
            [],
        ),
        (
            "Arbitrary but accepted SSM type",
            "AWS::SSM::Parameter::Value<AWS::FakeService::FakeResource>",
            [],
        ),
        (
            "Arbitrary but accepted List type",
            "List<AWS::FakeService::FakeResource>",
            [],
        ),
        (
            "Invalid type (not string)",
            [],
            [],
        ),
        (
            "Completely invalid type",
            "InvalidType",
            [
                ValidationError(
                    "'InvalidType' is not one of",
                    rule=Types(),
                )
            ],
        ),
        (
            "Typo in type",
            "Strng",
            [
                ValidationError(
                    "'Strng' is not one of",
                    rule=Types(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    if expected:
        assert len(errors) == len(expected), f"Test {name!r} got {errors!r}"
        for err, exp in zip(errors, expected):
            assert exp.message in err.message, f"Test {name!r} got {err.message!r}"
            assert err.rule.id == exp.rule.id
    else:
        assert errors == expected, f"Test {name!r} got {errors!r}"
