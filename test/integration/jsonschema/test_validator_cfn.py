"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
import unittest
from collections import deque
from typing import List

import jsonpatch

from cfnlint.decode import decode_str
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.template import Template


def build_template(patch: jsonpatch.JsonPatch | None) -> Template:
    """
    Build a template object from a dict
    """
    template_obj = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": ["true", {"Ref": "AWS::Region"}]},
            "IsNotUsEast1": {"Fn::Not": [{"Condition": "IsUsEast1"}]},
        },
        "Resources": {
            "MyResource": {
                "Type": "AWS::Test::Type",
                "Properties": {
                    "Name": "Name",
                    "Tags": [
                        {"Key": "Name", "Value": "Value"},
                    ],
                },
            }
        },
    }

    if patch is not None:
        jsonpatch.apply_patch(template_obj, patch, True)

    template, _ = decode_str(json.dumps(template_obj))
    if template:
        return Template("", template, regions=["us-east-1"])

    raise Exception("Template is invalid")


def build_schema(patch: jsonpatch.JsonPatch | None):
    schema = {
        "properties": {
            "Name": {
                "type": "string",
            },
            "Tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Key": {"type": "string"},
                        "Value": {"type": "string"},
                    },
                },
            },
        },
        "type": "object",
    }

    if patch is not None:
        jsonpatch.apply_patch(schema, patch, True)

    return schema


class TestValidatorCfnConditions(unittest.TestCase):
    """
    Integration testing of the CfnTemplateValidator class
    with a Template that allows us to exhaust scenario
    """

    def run_test(
        self,
        template_patches: jsonpatch.JsonPatch,
        schema_patches: jsonpatch.JsonPatch,
        expected_errs: List[ValidationError],
    ):
        """
        Run the test
        """
        cfn = build_template(template_patches)
        schema = build_schema(schema_patches)

        props = (
            cfn.template.get("Resources", {})
            .get("MyResource", {})
            .get("Properties", {})
        )

        context = cfn.context.evolve(functions=FUNCTIONS)
        validator = CfnTemplateValidator(schema=schema, cfn=cfn, context=context)
        errs = list(validator.iter_errors(props))

        self.assertEqual(len(errs), len(expected_errs), f"Received: {errs!r}")
        for i, err in enumerate(errs):
            self.assertEqual(expected_errs[i].message, err.message)
            self.assertEqual(expected_errs[i].path, err.path)
            self.assertEqual(expected_errs[i].validator, err.validator)
            self.assertEqual(expected_errs[i].validator_value, err.validator_value)

    def test_required(self):
        schema_patch = jsonpatch.JsonPatch(
            patch=[{"op": "add", "path": "/required", "value": ["Name"]}],
        )
        self.run_test(
            template_patches=None,
            schema_patches=schema_patch,
            expected_errs=[],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                patch=[
                    {"op": "remove", "path": "/Resources/MyResource/Properties/Name"}
                ],
            ),
            schema_patches=schema_patch,
            expected_errs=[
                ValidationError(
                    "'Name' is a required property",
                    validator="required",
                    validator_value=["Name"],
                ),
            ],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                patch=[
                    {
                        "op": "replace",
                        "path": "/Resources/MyResource/Properties/Name",
                        "value": {
                            "Fn::If": [
                                "IsUsEast1",
                                "Name",
                                {"Ref": "AWS::NoValue"},
                            ]
                        },
                    }
                ],
            ),
            schema_patches=schema_patch,
            expected_errs=[
                ValidationError(
                    "'Name' is a required property",
                    validator="required",
                    validator_value=["Name"],
                ),
            ],
        )

    def test_unique_items(self):
        schema_patch = jsonpatch.JsonPatch(
            [
                {"op": "add", "path": "/properties/Tags/uniqueItems", "value": True},
            ]
        )
        self.run_test(
            template_patches=None,
            schema_patches=schema_patch,
            expected_errs=[],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {
                        "op": "add",
                        "path": "/Resources/MyResource/Properties/Tags/-",
                        "value": {"Key": "Name", "Value": "Value"},
                    },
                ]
            ),
            schema_patches=schema_patch,
            expected_errs=[
                ValidationError(
                    message=(
                        "[{'Key': 'Name', 'Value': 'Value'}, "
                        "{'Key': 'Name', 'Value': 'Value'}] has "
                        "non-unique elements"
                    ),
                    path=deque(["Tags"]),
                    validator="uniqueItems",
                    validator_value=True,
                ),
            ],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {
                        "op": "add",
                        "path": "/Resources/MyResource/Properties/Tags/-",
                        "value": {
                            "Fn::If": [
                                "IsUsEast1",
                                {"Key": "Name", "Value": "Value"},
                                {"Key": "Foo", "Value": "Bar"},
                            ]
                        },
                    },
                ]
            ),
            schema_patches=schema_patch,
            expected_errs=[
                ValidationError(
                    message=(
                        "[{'Key': 'Name', 'Value': 'Value'}, "
                        "{'Key': 'Name', 'Value': 'Value'}] has "
                        "non-unique elements"
                    ),
                    path=deque(["Tags"]),
                    validator="uniqueItems",
                    validator_value=True,
                ),
            ],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {
                        "op": "replace",
                        "path": "/Resources/MyResource/Properties/Tags",
                        "value": [
                            {
                                "Fn::If": [
                                    "IsUsEast1",
                                    {"Key": "Name", "Value": "Value"},
                                    {"Ref": "AWS::NoValue"},
                                ],
                            },
                            {
                                "Fn::If": [
                                    "IsUsEast1",
                                    {"Ref": "AWS::NoValue"},
                                    {"Key": "Name", "Value": "Value"},
                                ],
                            },
                        ],
                    },
                ]
            ),
            schema_patches=schema_patch,
            expected_errs=[],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {
                        "op": "replace",
                        "path": "/Resources/MyResource/Properties/Tags",
                        "value": [
                            {
                                "Fn::If": [
                                    "IsUsEast1",
                                    {"Key": "Name", "Value": "Value"},
                                    {"Ref": "AWS::NoValue"},
                                ],
                            },
                            {
                                "Fn::If": [
                                    "IsNotUsEast1",
                                    {"Ref": "AWS::NoValue"},
                                    {"Key": "Name", "Value": "Value"},
                                ],
                            },
                        ],
                    },
                ]
            ),
            schema_patches=schema_patch,
            expected_errs=[
                ValidationError(
                    message=(
                        "[{'Key': 'Name', 'Value': 'Value'}, "
                        "{'Key': 'Name', 'Value': 'Value'}] has "
                        "non-unique elements"
                    ),
                    path=deque(["Tags"]),
                    validator="uniqueItems",
                    validator_value=True,
                ),
            ],
        )

    def test_dependencies(self):
        schema_patch = jsonpatch.JsonPatch(
            [
                {"op": "add", "path": "/dependencies", "value": {"Name": ["Tags"]}},
            ]
        )
        self.run_test(
            template_patches=None,
            schema_patches=schema_patch,
            expected_errs=[],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {"op": "remove", "path": "/Resources/MyResource/Properties/Tags"},
                ]
            ),
            schema_patches=schema_patch,
            expected_errs=[
                ValidationError(
                    message="'Tags' is a dependency of 'Name'",
                    path=deque([]),
                    validator="dependencies",
                    validator_value={"Name": ["Tags"]},
                ),
            ],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {
                        "op": "replace",
                        "path": "/Resources/MyResource/Properties/Tags",
                        "value": {
                            "Fn::If": [
                                "IsUsEast1",
                                {"Ref": "AWS::NoValue"},
                                [
                                    {
                                        "Fn::If": [
                                            "IsUsEast1",
                                            {"Ref": "AWS::NoValue"},
                                            {"Key": "Name", "Value": "Value"},
                                        ]
                                    },
                                ],
                            ]
                        },
                    },
                ]
            ),
            schema_patches=schema_patch,
            expected_errs=[
                ValidationError(
                    message="'Tags' is a dependency of 'Name'",
                    path=deque([]),
                    validator="dependencies",
                    validator_value={"Name": ["Tags"]},
                ),
            ],
        )
