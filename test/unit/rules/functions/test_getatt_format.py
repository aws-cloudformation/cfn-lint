"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.GetAttFormat import GetAttFormat


@pytest.fixture(scope="module")
def rule():
    rule = GetAttFormat()
    rule._exceptions = ["AWS::EC2::SecurityGroup.Id"]
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyBucket": {"Type": "AWS::S3::Bucket"},
            "MyVpc": {"Type": "AWS::EC2::VPC"},
            "MySecurityGroup": {"Type": "AWS::EC2::SecurityGroup"},
            "MyCustomResource": {"Type": "Custom::CustomResource"},
            "MySubTemplate": {"Type": "AWS::CloudFormation::Stack"},
            "MyProvisionedProduct": {
                "Type": "AWS::ServiceCatalog::CloudFormationProvisionedProduct"
            },
            "MySSMParameter": {"Type": "AWS::SSM::Parameter"},
        },
    }


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid GetAtt with a good format",
            ["MyVpc", "VpcId"],
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Valid GetAtt to a custom resource",
            ["MyCustomResource", "ImageId"],
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Valid GetAtt to a sub template ",
            ["MySubTemplate", "Outputs.ImageId"],
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Valid GetAtt to a provisioned product ",
            ["MyProvisionedProduct", "Outputs.VpcId"],
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Valid GetAtt because of exception",
            ["MyBucket", "Arn"],
            {"format": "AWS::EC2::SecurityGroup.Id"},
            [],
        ),
        (
            "Valid GetAtt because of exception with attribute",
            ["MySSMParameter", "Value"],
            {"format": "AWS::EC2::Image.Id"},
            [],
        ),
        (
            "Invalid GetAtt with a bad format",
            ["MyBucket", "Arn"],
            {"format": "AWS::EC2::VPC.Id"},
            [
                ValidationError(
                    (
                        "{'Fn::GetAtt': ['MyBucket', 'Arn']} "
                        "does not match destination format of 'AWS::EC2::VPC.Id'"
                    ),
                    rule=GetAttFormat(),
                )
            ],
        ),
        (
            "Invalid GetAtt with a getatt and no format",
            ["MyBucket", "WebsiteURL"],
            {"format": "AWS::EC2::VPC.Id"},
            [
                ValidationError(
                    (
                        "{'Fn::GetAtt': ['MyBucket', 'WebsiteURL']} "
                        "with formats ['uri'] does not match "
                        "destination format of 'AWS::EC2::VPC.Id'"
                    ),
                    rule=GetAttFormat(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.validate(validator, schema, instance, schema))
    assert errs == expected, f"Test {name!r} got {errs!r}"
