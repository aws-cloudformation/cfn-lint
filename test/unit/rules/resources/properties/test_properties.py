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
    "template",
    [
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
        }
    ],
    indirect=True,
)
def test_validate_with_unsatisfiable_condition(rule, validator):
    # Regression test for https://github.com/aws-cloudformation/cfn-lint/issues/4785
    # A resource whose own condition can never be true (here `X and not X`
    # over two identical conditions) must not raise Unsatisfiable (previously
    # surfaced as an E3001 exception); its property errors are reported the
    # same way as on an ungated resource.
    instance = {
        "Type": "MyType",
        "Condition": "OnAndNotEnabled",
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
    assert not any("raised while validating" in message for message in messages), (
        f"crash surfaced: {messages!r}"
    )


def _scaling_policy_schema_manager():
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = [
        (
            ["us-east-1"],
            Schema(
                {
                    "typeName": "AWS::ApplicationAutoScaling::ScalingPolicy",
                    "properties": {
                        "PolicyName": {"type": "string"},
                        "PolicyType": {"type": "string"},
                        "ScalingTargetId": {"type": "string"},
                        "ResourceId": {"type": "string"},
                        "ScalableDimension": {"type": "string"},
                        "ServiceNamespace": {"type": "string"},
                    },
                    "required": ["PolicyName", "PolicyType"],
                    "requiredXor": ["ScalingTargetId", "ResourceId"],
                    "dependentRequired": {
                        "ResourceId": ["ScalableDimension", "ServiceNamespace"]
                    },
                }
            ),
        )
    ]
    return schema_manager


def _scaling_policy_properties(**overrides):
    properties = {
        "PolicyName": "MyPolicy",
        "PolicyType": "TargetTrackingScaling",
    }
    properties.update(overrides)
    return {
        "Type": "AWS::ApplicationAutoScaling::ScalingPolicy",
        "Properties": properties,
    }


@pytest.mark.parametrize(
    "name,properties,expected_validators",
    [
        # Both ScalingTargetId and the trio may be specified together, the
        # requiredXor violation is a false positive (consistency is checked
        # by rule E3726 instead)
        (
            "ScalingTargetId and complete trio",
            {
                "ScalingTargetId": {"Ref": "Target"},
                "ResourceId": "table/my-table",
                "ScalableDimension": "dynamodb:table:WriteCapacityUnits",
                "ServiceNamespace": "dynamodb",
            },
            [],
        ),
        # Both specified but disagreeing: still no requiredXor error, the
        # mismatch itself is reported by rule E3726
        (
            "ScalingTargetId and mismatching trio",
            {
                "ScalingTargetId": {"Ref": "Target"},
                "ResourceId": "table/other-table",
                "ScalableDimension": "dynamodb:table:WriteCapacityUnits",
                "ServiceNamespace": "dynamodb",
            },
            [],
        ),
        # Only the complete trio: valid, unchanged behavior
        (
            "Complete trio only",
            {
                "ResourceId": "table/my-table",
                "ScalableDimension": "dynamodb:table:WriteCapacityUnits",
                "ServiceNamespace": "dynamodb",
            },
            [],
        ),
        # Only ScalingTargetId: valid, unchanged behavior
        (
            "ScalingTargetId only",
            {"ScalingTargetId": {"Ref": "Target"}},
            [],
        ),
        # Neither group: the "at least one complete group" requirement
        # still errors
        (
            "Neither ScalingTargetId nor ResourceId",
            {},
            ["requiredXor"],
        ),
        # An incomplete trio alone: dependentRequired still errors
        (
            "Incomplete trio alone",
            {"ResourceId": "table/my-table"},
            ["dependentRequired"],
        ),
    ],
)
def test_validate_scaling_policy_required_xor(
    name, properties, expected_validators, rule, validator
):
    instance = _scaling_policy_properties(**properties)
    schema_manager = _scaling_policy_schema_manager()

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

    validators = sorted({err.validator for err in errs})
    assert validators == expected_validators, (
        f"Test {name!r} expected validators {expected_validators!r} "
        f"got {validators!r}: {[e.message for e in errs]!r}"
    )
