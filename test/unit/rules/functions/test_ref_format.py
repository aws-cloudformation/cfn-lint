"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.RefFormat import RefFormat


@pytest.fixture(scope="module")
def rule():
    rule = RefFormat()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyBucket": {"Type": "AWS::S3::Bucket"},
            "MyVpc": {"Type": "AWS::EC2::VPC"},
            "MyCustomResource": {"Type": "Custom::MyResource"},
        },
    }


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Ref with a good format",
            "MyVpc",
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Valid Ref with a good format",
            "MyCustomResource",
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Invalid Ref with a bad format",
            "MyVpc",
            {"format": "AWS::EC2::Image.Id"},
            [
                ValidationError(
                    (
                        "{'Ref': 'MyVpc'} with formats "
                        "['AWS::EC2::VPC.Id'] does not match "
                        "destination format of 'AWS::EC2::Image.Id'"
                    ),
                    rule=RefFormat(),
                )
            ],
        ),
        (
            "Invalid Ref with a resource with no format",
            "MyBucket",
            {"format": "AWS::EC2::Image.Id"},
            [
                ValidationError(
                    (
                        "{'Ref': 'MyBucket'} does not match "
                        "destination format of 'AWS::EC2::Image.Id'"
                    ),
                    rule=RefFormat(),
                )
            ],
        ),
        (
            "Invalid Ref to non existent resource",
            "DNE",
            {"format": "AWS::EC2::Image.Id"},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.validate(validator, schema, instance, schema))
    assert errs == expected, f"Test {name!r} got {errs!r}"
