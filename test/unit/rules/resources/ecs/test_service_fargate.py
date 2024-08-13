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
from cfnlint.rules.resources.ecs.ServiceFargate import ServiceFargate


@pytest.fixture
def rule():
    rule = ServiceFargate()
    yield rule


_task_definition = {
    "Type": "AWS::ECS::TaskDefinition",
    "Properties": {
        "RequiresCompatibilities": ["FARGATE"],
    },
}

_service = {
    "Type": "AWS::ECS::Service",
    "Properties": {
        "TaskDefinition": {"Ref": "TaskDefinition"},
        "LaunchType": "FARGATE",
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
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Fn::Sub": "${TaskDefinition.Arn}"},
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
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
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
                    ("'RequiresCompatibilities' is a required property"),
                    validator="required",
                    rule=ServiceFargate(),
                    path_override=deque(["Resources", "TaskDefinition", "Properties"]),
                )
            ],
        ),
        (
            {
                "Parameters": {"MyTask": {"Type": "String"}},
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Ref": "MyTask"},
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
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": "MyTask",
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
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    ("'RequiresCompatibilities' is a required property"),
                    validator="required",
                    rule=ServiceFargate(),
                    path_override=deque(["Resources", "TaskDefinition", "Properties"]),
                )
            ],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/LaunchType",
                                "value": "EC2",
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
                                "path": "/Properties/RequiresCompatibilities",
                                "value": [
                                    "EC2",
                                    "FARGATE",
                                ],
                            },
                        ],
                    ),
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
                                "op": "replace",
                                "path": "/Properties/RequiresCompatibilities",
                                "value": [
                                    "EC2",
                                    "EXTERNAL",
                                ],
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    ("['EC2', 'EXTERNAL'] does not contain items matching 'FARGATE'"),
                    validator="contains",
                    rule=ServiceFargate(),
                    path_override=deque(
                        [
                            "Resources",
                            "TaskDefinition",
                            "Properties",
                            "RequiresCompatibilities",
                        ]
                    ),
                )
            ],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/RequiresCompatibilities",
                                "value": {"Fn::FindInMap": ["A", "B", "C"]},
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        (
            {
                "Parameters": {"MyLaunchType": {"Type": "String"}},
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/RequiresCompatibilities",
                                "value": ["EC2", {"Ref": "MyLaunchType"}],
                            },
                        ],
                    ),
                    "Service": dict(_service),
                },
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
                                "op": "add",
                                "path": "/Properties/NetworkMode",
                                "value": "awsvpc",
                            },
                            {
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                },
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
                                "op": "add",
                                "path": "/Properties/NetworkMode",
                                "value": {"Ref": "MyNetworkMode"},
                            },
                            {
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                },
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
                                "op": "add",
                                "path": "/Properties/NetworkMode",
                                "value": "host",
                            },
                            {
                                "op": "remove",
                                "path": "/Properties/RequiresCompatibilities",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                },
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    ("'RequiresCompatibilities' is a required property"),
                    validator="required",
                    rule=ServiceFargate(),
                    path_override=deque(["Resources", "TaskDefinition", "Properties"]),
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
