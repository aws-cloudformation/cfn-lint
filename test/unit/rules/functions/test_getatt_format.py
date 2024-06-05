"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.GetAttFormat import GetAttFormat
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = GetAttFormat()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Resources": {
                "MyBucket": {"Type": "AWS::S3::Bucket"},
                "MyVpc": {"Type": "AWS::EC2::VPC"},
                "MySecurityGroup": {"Type": "AWS::EC2::SecurityGroup"},
            },
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.fixture(scope="module")
def validator(cfn, context):
    return CfnTemplateValidator({}, context=context, cfn=cfn)


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
            "Valid GetAtt because of exception",
            ["MyBucket", "Arn"],
            {"format": "AWS::EC2::SecurityGroup.GroupId"},
            [],
        ),
        (
            "Invalid GetAtt with a bad format",
            ["MyBucket", "Arn"],
            {"format": "AWS::EC2::VPC.Id"},
            [
                ValidationError(
                    (
                        "{'Fn::GetAtt': ['MyBucket', 'Arn']} that "
                        "does not match 'AWS::EC2::VPC.Id'"
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
