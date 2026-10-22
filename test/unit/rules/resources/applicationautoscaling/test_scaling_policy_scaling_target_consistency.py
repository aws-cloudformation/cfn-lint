"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import jsonpatch
import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.applicationautoscaling import (
    ScalingPolicyScalingTargetConsistency as _consistency_module,
)

ScalingPolicyScalingTargetConsistency = (
    _consistency_module.ScalingPolicyScalingTargetConsistency
)


@pytest.fixture
def rule():
    rule = ScalingPolicyScalingTargetConsistency()
    yield rule


def _message(prop, value):
    return (
        f"{prop} {value!r} does not match ScalingTargetId. "
        "When both ScalingTargetId and ResourceId are specified, "
        "ResourceId, ScalableDimension, and ServiceNamespace must agree "
        "with the referenced AWS::ApplicationAutoScaling::ScalableTarget."
    )


def _expected_error(prop, value):
    return ValidationError(
        _message(prop, value),
        validator="const",
        rule=ScalingPolicyScalingTargetConsistency(),
        path=deque([prop]),
        schema_path=deque(
            [
                "cfnGather",
                "schema",
                "then",
                "properties",
                "policy",
                "properties",
                prop,
                "const",
            ]
        ),
    )


_target = {
    "Type": "AWS::ApplicationAutoScaling::ScalableTarget",
    "Properties": {
        "MaxCapacity": 4,
        "MinCapacity": 1,
        "ResourceId": "table/my-table",
        "ScalableDimension": "dynamodb:table:WriteCapacityUnits",
        "ServiceNamespace": "dynamodb",
    },
}

_policy = {
    "Type": "AWS::ApplicationAutoScaling::ScalingPolicy",
    "Properties": {
        "PolicyName": "MyPolicy",
        "PolicyType": "TargetTrackingScaling",
        "ScalingTargetId": {"Ref": "Target"},
        "ResourceId": "table/my-table",
        "ScalableDimension": "dynamodb:table:WriteCapacityUnits",
        "ServiceNamespace": "dynamodb",
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # Valid - ScalingTargetId and the trio agree
        (
            {
                "Resources": {
                    "Target": dict(_target),
                    "Policy": dict(_policy),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - agreement via Fn::GetAtt to the target
        (
            {
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ScalingTargetId",
                                "value": {"Fn::GetAtt": ["Target", "Id"]},
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Invalid - ResourceId does not match the referenced target
        (
            {
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ResourceId",
                                "value": "table/other-table",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [_expected_error("ResourceId", "table/other-table")],
        ),
        # Invalid - ScalableDimension does not match the referenced target
        (
            {
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ScalableDimension",
                                "value": "dynamodb:table:ReadCapacityUnits",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [_expected_error("ScalableDimension", "dynamodb:table:ReadCapacityUnits")],
        ),
        # Invalid - ServiceNamespace does not match the referenced target
        (
            {
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ServiceNamespace",
                                "value": "ecs",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [_expected_error("ServiceNamespace", "ecs")],
        ),
        # Invalid - all three trio values disagree, one error per property
        (
            {
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ResourceId",
                                "value": "table/other-table",
                            },
                            {
                                "op": "replace",
                                "path": "/Properties/ScalableDimension",
                                "value": "dynamodb:table:ReadCapacityUnits",
                            },
                            {
                                "op": "replace",
                                "path": "/Properties/ServiceNamespace",
                                "value": "ecs",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [
                _expected_error("ResourceId", "table/other-table"),
                _expected_error(
                    "ScalableDimension", "dynamodb:table:ReadCapacityUnits"
                ),
                _expected_error("ServiceNamespace", "ecs"),
            ],
        ),
        # Valid - only the trio is specified, nothing to compare
        (
            {
                "Resources": {
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/ScalingTargetId",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - only ScalingTargetId is specified, nothing to compare
        (
            {
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {"op": "remove", "path": "/Properties/ResourceId"},
                            {"op": "remove", "path": "/Properties/ScalableDimension"},
                            {"op": "remove", "path": "/Properties/ServiceNamespace"},
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - incomplete trio alone, schema rules still own this case
        (
            {
                "Resources": {
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/ScalingTargetId",
                            },
                            {
                                "op": "remove",
                                "path": "/Properties/ServiceNamespace",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - ScalingTargetId references a parameter, cannot resolve
        (
            {
                "Parameters": {"TargetParam": {"Type": "String"}},
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ScalingTargetId",
                                "value": {"Ref": "TargetParam"},
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - ScalingTargetId is a hardcoded string, cannot resolve
        (
            {
                "Resources": {
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ScalingTargetId",
                                "value": "target-id-1234",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - ScalingTargetId references a resource that is not a
        # scalable target, cannot compare
        (
            {
                "Resources": {
                    "Topic": {"Type": "AWS::SNS::Topic"},
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ScalingTargetId",
                                "value": {"Ref": "Topic"},
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - target values use functions and cannot be resolved
        (
            {
                "Parameters": {"TableName": {"Type": "String"}},
                "Resources": {
                    "Target": jsonpatch.apply_patch(
                        dict(_target),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ResourceId",
                                "value": {"Ref": "TableName"},
                            },
                        ],
                    ),
                    "Policy": dict(_policy),
                },
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - policy trio values use functions and cannot be resolved
        (
            {
                "Parameters": {"TableName": {"Type": "String"}},
                "Resources": {
                    "Target": dict(_target),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ResourceId",
                                "value": {"Ref": "TableName"},
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"
