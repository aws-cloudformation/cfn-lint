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
from cfnlint.rules.resources.autoscaling.ScalingPolicyTargetTrackingAsg import (
    ScalingPolicyTargetTrackingAsg,
)


@pytest.fixture
def rule():
    rule = ScalingPolicyTargetTrackingAsg()
    yield rule


_asg = {
    "Type": "AWS::AutoScaling::AutoScalingGroup",
    "Properties": {
        "MinSize": "1",
        "MaxSize": "5",
    },
}

_policy = {
    "Type": "AWS::AutoScaling::ScalingPolicy",
    "Properties": {
        "AutoScalingGroupName": {"Ref": "ASG"},
        "PolicyType": "TargetTrackingScaling",
        "TargetTrackingConfiguration": {
            "PredefinedMetricSpecification": {
                "PredefinedMetricType": "ASGAverageCPUUtilization",
            },
            "TargetValue": 50.0,
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # Valid - MaxSize != MinSize with TargetTrackingScaling
        (
            {
                "Resources": {
                    "ASG": dict(_asg),
                    "Policy": dict(_policy),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - StepScaling with MaxSize == MinSize is fine
        (
            {
                "Resources": {
                    "ASG": jsonpatch.apply_patch(
                        dict(_asg),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/MaxSize",
                                "value": "1",
                            },
                        ],
                    ),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/PolicyType",
                                "value": "StepScaling",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - Ref to parameter (not a resource), skip validation
        (
            {
                "Parameters": {"MyASG": {"Type": "String"}},
                "Resources": {
                    "ASG": jsonpatch.apply_patch(
                        dict(_asg),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/MaxSize",
                                "value": "1",
                            },
                        ],
                    ),
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/AutoScalingGroupName",
                                "value": {"Ref": "MyASG"},
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - hardcoded string ASG name, skip validation
        (
            {
                "Resources": {
                    "Policy": jsonpatch.apply_patch(
                        dict(_policy),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/AutoScalingGroupName",
                                "value": "my-asg",
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Valid - non-numeric values (Ref) for MaxSize, skip
        (
            {
                "Resources": {
                    "ASG": jsonpatch.apply_patch(
                        dict(_asg),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/MaxSize",
                                "value": {"Ref": "Param"},
                            },
                        ],
                    ),
                    "Policy": dict(_policy),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [],
        ),
        # Invalid - TargetTrackingScaling with MaxSize == MinSize
        (
            {
                "Resources": {
                    "ASG": jsonpatch.apply_patch(
                        dict(_asg),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/MaxSize",
                                "value": "1",
                            },
                        ],
                    ),
                    "Policy": dict(_policy),
                }
            },
            deque(["Resources", "Policy", "Properties"]),
            [
                ValidationError(
                    (
                        "TargetTrackingScaling policy requires the referenced "
                        "AutoScalingGroup to have MaxSize greater than MinSize"
                    ),
                    validator="exclusiveMinimum",
                    rule=ScalingPolicyTargetTrackingAsg(),
                    path_override=deque(["Resources", "ASG", "Properties", "MaxSize"]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "asg",
                            "properties",
                            "MaxSize",
                            "exclusiveMinimum",
                        ]
                    ),
                )
            ],
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
