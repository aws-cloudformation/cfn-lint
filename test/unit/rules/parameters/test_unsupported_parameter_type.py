"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.parameters.UnsupportedParameterType import UnsupportedParameterType


@pytest.fixture(scope="module")
def rule():
    rule = UnsupportedParameterType()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid supported type",
            "AWS::EC2::VPC::Id",
            [],
        ),
        (
            "Valid supported SSM type",
            "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
            [],
        ),
        (
            "Valid supported List type",
            "List<AWS::EC2::Subnet::Id>",
            [],
        ),
        (
            "Invalid type (not string)",
            [],
            [],
        ),
        (
            "Unsupported SSM PrefixList type",
            "AWS::SSM::Parameter::Value<AWS::EC2::PrefixList::Id>",
            [
                ValidationError(
                    "'AWS::SSM::Parameter::Value<AWS::EC2::PrefixList::Id>' "
                    "is not an officially documented CloudFormation "
                    "parameter type. While CloudFormation may accept this "
                    "type, it will not validate the parameter value.",
                    rule=UnsupportedParameterType(),
                )
            ],
        ),
        (
            "Unsupported SSM SecurityGroup type",
            "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup>",
            [
                ValidationError(
                    "'AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup>' "
                    "is not an officially documented CloudFormation "
                    "parameter type. While CloudFormation may accept this "
                    "type, it will not validate the parameter value.",
                    rule=UnsupportedParameterType(),
                )
            ],
        ),
        (
            "Unsupported SSM Lambda ARN type",
            "AWS::SSM::Parameter::Value<AWS::Lambda::Function::Arn>",
            [
                ValidationError(
                    "'AWS::SSM::Parameter::Value<AWS::Lambda::Function::Arn>' "
                    "is not an officially documented CloudFormation "
                    "parameter type. While CloudFormation may accept this "
                    "type, it will not validate the parameter value.",
                    rule=UnsupportedParameterType(),
                )
            ],
        ),
        (
            "Arbitrary SSM type",
            "AWS::SSM::Parameter::Value<AWS::FakeService::FakeResource>",
            [
                ValidationError(
                    "'AWS::SSM::Parameter::Value<AWS::FakeService::FakeResource>' "
                    "is not an officially documented CloudFormation "
                    "parameter type. While CloudFormation may accept this "
                    "type, it will not validate the parameter value.",
                    rule=UnsupportedParameterType(),
                )
            ],
        ),
        (
            "Arbitrary List type",
            "List<AWS::FakeService::FakeResource>",
            [
                ValidationError(
                    "'List<AWS::FakeService::FakeResource>' is not an "
                    "officially documented CloudFormation parameter type. "
                    "While CloudFormation may accept this type, it will not "
                    "validate the parameter value.",
                    rule=UnsupportedParameterType(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    assert errors == expected, f"Test {name!r} got {errors!r}"
