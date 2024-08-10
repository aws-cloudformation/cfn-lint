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
from cfnlint.rules.resources.ecs.ServiceNetworkConfiguration import (
    ServiceNetworkConfiguration,
)


@pytest.fixture
def rule():
    rule = ServiceNetworkConfiguration()
    yield rule


_task_definition = {
    "Type": "AWS::ECS::TaskDefinition",
    "Properties": {
        "NetworkMode": "awsvpc",
        "ContainerDefinitions": [],
    },
}

_service = {
    "Type": "AWS::ECS::Service",
    "Properties": {
        "TaskDefinition": {"Ref": "TaskDefinition"},
        "NetworkConfiguration": {},
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkMode",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/NetworkMode",
                                "value": "bridge",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        (
            {
                "Parameters": {"MyNetworkMode": {"Type": "String"}},
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/NetworkMode",
                                "value": {"Ref": "MyNetworkMode"},
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    ("'NetworkConfiguration' is a required property"),
                    validator="required",
                    rule=ServiceNetworkConfiguration(),
                )
            ],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Fn::GetAtt": "TaskDefinition.Arn"},
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    ("'NetworkConfiguration' is a required property"),
                    validator="required",
                    rule=ServiceNetworkConfiguration(),
                )
            ],
        ),
        (
            {
                "Parameters": {"MyTargetGroup": {"Type": "String"}},
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Ref": "MyTargetGroup"},
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Foo": "Bar"},
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/NetworkConfiguration",
                            },
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Fn::Sub": "${TaskDefinition.Arn}"},
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Service", "Properties"]),
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
