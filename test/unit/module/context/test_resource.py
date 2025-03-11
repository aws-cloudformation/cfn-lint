"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest.mock import patch

import pytest

from cfnlint.context.context import Resource, _init_resources
from cfnlint.match import Match
from cfnlint.rules.errors.parse import ParseError
from cfnlint.schema import AttributeDict


@pytest.mark.parametrize(
    "name,instance,expected_ref",
    [
        (
            "Valid resource",
            {"Type": "AWS::EC2::VPC"},
            {"format": "AWS::EC2::VPC.Id", "type": "string"},
        ),
    ],
)
def test_resource(name, instance, expected_ref):
    region = "us-east-1"
    resource = Resource(instance)

    assert expected_ref == resource.ref(
        region
    ), f"{name!r} test got {resource.ref(region)}"


@pytest.mark.parametrize(
    "name,instance",
    [
        ("Invalid Type", {"Type": {}}),
    ],
)
def test_errors(name, instance):
    with pytest.raises(ValueError):
        Resource(instance)


def test_resources():
    with pytest.raises(ValueError):
        _init_resources([])


@pytest.mark.parametrize(
    "name,instance,decode_results,expected_getatts",
    [
        (
            "Nested stack with no Properties",
            {"Type": "AWS::CloudFormation::Stack"},
            None,
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with template URL",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "https://bucket/path.yaml"},
            },
            None,
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a local file",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            ({"Outputs": {"MyValue": {"Type": "String"}}}, None),
            AttributeDict({"Outputs.MyValue": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a local file and no outputs",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            ({}, None),
            AttributeDict({}),
        ),
        (
            "Nested stack with a local file but match error",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            (None, Match("test", rule=ParseError())),
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
    ],
)
def test_nested_stacks(name, instance, decode_results, expected_getatts):
    region = "us-east-1"
    filename = "foo/bar.yaml"

    with patch("cfnlint.decode.decode") as mock_decode:
        if decode_results is not None:
            mock_decode.return_value = decode_results

        resource = Resource(instance, filename)

        assert expected_getatts == resource.get_atts(
            region
        ), f"{name!r} test got {resource.get_atts(region)}"
