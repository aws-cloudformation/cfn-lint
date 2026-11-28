"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
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


@pytest.mark.parametrize(
    "template,condition",
    [
        (
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Conditions": {
                    "IsFeatureOn": {"Fn::Equals": ["false", "true"]},
                    "IsFeatureEnabled": {"Fn::Equals": ["false", "true"]},
                    "OnAndNotEnabled": {
                        "Fn::And": [
                            {"Condition": "IsFeatureOn"},
                            {"Fn::Not": [{"Condition": "IsFeatureEnabled"}]},
                        ]
                    },
                },
            },
            "OnAndNotEnabled",
        ),
        (
            # A constant Fn::Equals of two unequal literals can never be
            # true (issue #5074).
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Conditions": {
                    "NeverTrue": {"Fn::Equals": ["us-east-1", "us-west-2"]},
                },
            },
            "NeverTrue",
        ),
        (
            # A parameter can only take one of its AllowedValues, so a
            # comparison against a value outside the list can never be
            # true (issue #5075).
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Parameters": {
                    "Env": {
                        "Type": "String",
                        "Default": "prod",
                        "AllowedValues": ["prod"],
                    },
                },
                "Conditions": {
                    "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                },
            },
            "IsDev",
        ),
    ],
    indirect=["template"],
)
def test_validate_with_unsatisfiable_condition(rule, validator, condition):
    # Regression tests for
    # https://github.com/aws-cloudformation/cfn-lint/issues/4785 and
    # https://github.com/aws-cloudformation/cfn-lint/issues/5074
    # A resource whose own condition can never be true must not raise
    # Unsatisfiable (previously surfaced as an E3001 exception).  It is
    # not validated either: CloudFormation ignores entities associated
    # with a false condition and never evaluates their properties, so a
    # property error on such a resource cannot occur at deploy time.
    instance = {
        "Type": "MyType",
        "Condition": condition,
        "Properties": {"BogusProperty": 1},
    }
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = [
        (
            ["us-east-1"],
            Schema(
                {
                    "typeName": "MyType",
                    "properties": {},
                    "additionalProperties": False,
                }
            ),
        )
    ]

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

    messages = [e.message for e in errs]
    assert messages == [], f"dead resource was validated: {messages!r}"
    assert not any("raised while validating" in message for message in messages), (
        f"crash surfaced: {messages!r}"
    )


@pytest.mark.parametrize(
    "template",
    [
        {
            # Control for issue #5075: dev is an allowed value, so the
            # condition can be true and the resource is validated.
            "AWSTemplateFormatVersion": "2010-09-09",
            "Parameters": {
                "Env": {
                    "Type": "String",
                    "Default": "prod",
                    "AllowedValues": ["prod", "dev"],
                },
            },
            "Conditions": {
                "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
            },
        }
    ],
    indirect=True,
)
def test_validate_with_satisfiable_condition(rule, validator):
    # A resource whose condition can be true is validated as before.
    instance = {
        "Type": "MyType",
        "Condition": "IsDev",
        "Properties": {"BogusProperty": 1},
    }
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = [
        (
            ["us-east-1"],
            Schema(
                {
                    "typeName": "MyType",
                    "properties": {},
                    "additionalProperties": False,
                }
            ),
        )
    ]

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

    messages = [e.message for e in errs]
    assert any(
        "Additional properties are not allowed ('BogusProperty' was unexpected)"
        in message
        for message in messages
    ), f"property finding missing on gated resource: {messages!r}"
