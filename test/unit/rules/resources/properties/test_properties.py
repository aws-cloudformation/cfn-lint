"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from collections import deque
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.properties.Properties import Properties
from cfnlint.schema._schema import Schema


@pytest.fixture(scope="module")
def rule():
    rule = Properties()
    yield rule


@pytest.mark.parametrize(
    "name,instance,patches,expected",
    [
        (
            "Valid results",
            {
                "Type": "MyType",
            },
            [(["us-east-1"], Schema({"typeName": "MyType", "properties": {}}))],
            [],
        ),
        (
            "Invalid type for Type",
            {
                "Type": {},
            },
            [],
            [],
        ),
        (
            "Valid type but no required fields",
            {
                "Type": "MyType",
            },
            [(["us-east-1"], Schema({"typeName": "MyType", "required": ["Name"]}))],
            [
                ValidationError(
                    "'Name' is a required property",
                    validator="required",
                    path=deque(["Properties"]),
                    schema_path=deque(["required"]),
                )
            ],
        ),
        (
            "Invalid with Ref AWS::NoValue",
            {"Type": "MyType", "Properties": {"Ref": "AWS::NoValue"}},
            [],
            [
                ValidationError(
                    "{'Ref': 'AWS::NoValue'} is not of type object",
                    validator="type",
                    path=deque(["Properties", "Ref"]),
                    rule=None,
                )
            ],
        ),
        (
            "Invalid with Null value",
            {"Type": "AWS::S3::Bucket", "Properties": None},
            [],
            [
                ValidationError(
                    "None is not of type object",
                    validator="type",
                    path=deque(["Properties"]),
                    rule=None,
                )
            ],
        ),
    ],
)
def test_validate(name, instance, patches, expected, rule, validator):
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = patches

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

        assert errs == expected, f"Test {name!r} got {errs!r}"

    if patches:
        schema_manager.get_resource_schemas_by_regions.assert_called_once()
        schema_manager.get_resource_schemas_by_regions.assert_called_with(
            instance.get("Type"), ["us-east-1"]
        )
    else:
        schema_manager.get_resource_schemas_by_regions.assert_not_called()


def test_launch_template_network_performance_options_patch(rule, validator):
    schema = Schema(
        {
            "typeName": "AWS::EC2::LaunchTemplate",
            "properties": {
                "LaunchTemplateData": {
                    "$ref": "#/definitions/LaunchTemplateData",
                },
            },
            "definitions": {
                "LaunchTemplateData": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "ImageId": {"type": "string"},
                    },
                },
            },
        }
    )
    patch_path = Path(
        "src/cfnlint/data/schemas/patches/extensions/all/"
        "aws_ec2_launchtemplate/network_performance_options.json"
    )
    with patch_path.open(encoding="utf-8") as fh:
        schema.patch(json.load(fh))

    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = [
        (["us-east-1"], schema)
    ]

    instance = {
        "Type": "AWS::EC2::LaunchTemplate",
        "Properties": {
            "LaunchTemplateData": {
                "ImageId": "ami-1234567890abcdef0",
                "NetworkPerformanceOptions": {
                    "BandwidthWeighting": "vpc-1",
                },
            },
        },
    }

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        assert list(rule.validate(validator, {}, instance, {})) == []
