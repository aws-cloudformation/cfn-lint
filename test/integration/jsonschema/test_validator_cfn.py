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

from cfnlint.context import create_context_for_resource_properties
from cfnlint.decode import decode_str
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
    return Template("", template, regions=["us-east-1"])


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

        context = create_context_for_resource_properties(cfn, "us-east-1", "MyResource")
        validator = CfnTemplateValidator(schema=schema, cfn=cfn, context=context)
        errs = list(validator.iter_errors(props))

        self.assertEqual(len(errs), len(expected_errs))
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

    def test_ref(self):
        """
        Refs can be to resource parameters or pseudo parameters.
        We should be able to evaluate the errors that can come
        from those functions
        """
        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {
                        "op": "replace",
                        "path": "/Resources/MyResource/Properties/Name",
                        "value": {"Ref": "AWS::Region"},
                    },
                ]
            ),
            schema_patches=jsonpatch.JsonPatch(
                [
                    {"op": "add", "path": "/properties/Name/pattern", "value": "^foo$"},
                ]
            ),
            expected_errs=[
                ValidationError(
                    message=(
                        "{'Ref': 'AWS::Region'} does not match '^foo$' "
                        "when 'Ref' is resolved"
                    ),
                    path=deque(["Name", "Ref"]),
                    validator="ref",
                    validator_value="^foo$",
                ),
            ],
        )

        self.run_test(
            template_patches=jsonpatch.JsonPatch(
                [
                    {
                        "op": "add",
                        "path": "/Parameters",
                        "value": {
                            "Name": {
                                "Type": "String",
                                "Description": "Name",
                                "Default": "foo",
                                "AllowedValues": [
                                    "foo",
                                    "bar",
                                ],
                            }
                        },
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/MyResource/Properties/Name",
                        "value": {"Ref": "Name"},
                    },
                ]
            ),
            schema_patches=jsonpatch.JsonPatch(
                [
                    {"op": "add", "path": "/properties/Name/pattern", "value": "^bar$"},
                    {"op": "add", "path": "/properties/Name/enum", "value": ["bar"]},
                ]
            ),
            expected_errs=[
                ValidationError(
                    message=(
                        "{'Ref': 'Name'} does not match '^bar$' when 'Ref' is resolved"
                    ),
                    path=deque(["Name", "Ref"]),
                    validator="ref",
                    validator_value="^bar$",
                ),
                ValidationError(
                    message=(
                        "{'Ref': 'Name'} is not one of ['bar'] when 'Ref' is resolved"
                    ),
                    path=deque(["Name", "Ref"]),
                    validator="ref",
                    validator_value=["bar"],
                ),
                ValidationError(
                    message=(
                        "{'Ref': 'Name'} does not match '^bar$' when 'Ref' is resolved"
                    ),
                    path=deque(["Name", "Ref"]),
                    validator="ref",
                    validator_value="^bar$",
                ),
                ValidationError(
                    message=(
                        "{'Ref': 'Name'} is not one of ['bar'] when 'Ref' is resolved"
                    ),
                    path=deque(["Name", "Ref"]),
                    validator="ref",
                    validator_value=["bar"],
                ),
            ],
        )
