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
            "MyHostedZone": {"Type": "AWS::Route53::HostedZone"},
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
                    "{'Ref': 'MyVpc'} with formats "
                    "['AWS::EC2::VPC.Id'] does not match "
                    "destination format of 'AWS::EC2::Image.Id'",
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
                    "{'Ref': 'MyBucket'} with formats "
                    "['AWS::S3::Bucket.Name'] does not match "
                    "destination format of 'AWS::EC2::Image.Id'",
                    rule=RefFormat(),
                )
            ],
        ),
        (
            "Valid Ref of a hosted zone at a Route53 alias target (issue #4803)",
            "MyHostedZone",
            {"format": "AWS::Route53::AliasTarget.HostedZoneId"},
            [],
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


def test_validate_alias_target_rejects_unrelated_ref(rule, validator):
    # A Ref that returns an unrelated value must still raise E1041 at
    # AliasTarget.HostedZoneId, even with the #4803 format alias in place.
    # The exact wording of the destination format is not pinned: the
    # comparer reports the canonical (aliased) format name.
    schema = {"format": "AWS::Route53::AliasTarget.HostedZoneId"}
    errs = list(rule.validate(validator, schema, "MyVpc", schema))
    assert len(errs) == 1
    assert isinstance(errs[0].rule, RefFormat)
    assert "'Ref': 'MyVpc'" in errs[0].message
    assert "does not match destination format" in errs[0].message
