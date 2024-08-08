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
from cfnlint.rules.resources.ecs.TaskDefinitionAwsVpc import TaskDefinitionAwsVpc


@pytest.fixture
def rule():
    rule = TaskDefinitionAwsVpc()
    yield rule


_task_definition = {
    "Type": "AWS::ECS::TaskDefinition",
    "Properties": {
        "NetworkMode": "awsvpc",
        "ContainerDefinitions": [
            {
                "Name": "my-container",
                "Image": "my-image",
                "PortMappings": [
                    {
                        "ContainerPort": 8080,
                    }
                ],
            }
        ],
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                }
            },
            deque(["Resources", "TaskDefinition", "Properties"]),
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
                                "path": (
                                    "/Properties/ContainerDefinitions/"
                                    "0/PortMappings/0/HostPort"
                                ),
                                "value": "8080",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "TaskDefinition", "Properties"]),
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
                                "path": (
                                    "/Properties/ContainerDefinitions/"
                                    "0/PortMappings/0/HostPort"
                                ),
                                "value": "8080",
                            },
                            {
                                "op": "replace",
                                "path": (
                                    "/Properties/ContainerDefinitions/"
                                    "0/PortMappings/0/ContainerPort"
                                ),
                                "value": {"Fn::Sub": "8080"},
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "TaskDefinition", "Properties"]),
            [],
        ),
        (
            {
                "Parameters": {
                    "MyPort": {"Type": "String"},
                    "MySecondPort": {"Type": "String"},
                },
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "add",
                                "path": (
                                    "/Properties/ContainerDefinitions/0"
                                    "/PortMappings/0/ContainerPort"
                                ),
                                "value": {"Ref": "MyPort"},
                            },
                            {
                                "op": "add",
                                "path": (
                                    "/Properties/ContainerDefinitions/0"
                                    "/PortMappings/0/HostPort"
                                ),
                                "value": {"Ref": "MySecondPort"},
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "TaskDefinition", "Properties"]),
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
                                "path": (
                                    "/Properties/ContainerDefinitions/0"
                                    "/PortMappings/0/HostPort"
                                ),
                                "value": "80",
                            },
                            {
                                "op": "replace",
                                "path": ("/Properties/NetworkMode"),
                                "value": "bridge",
                            },
                        ],
                    ),
                }
            },
            deque(["Resources", "TaskDefinition", "Properties"]),
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
                                "path": (
                                    "/Properties/ContainerDefinitions/0"
                                    "/PortMappings/0/HostPort"
                                ),
                                "value": "80",
                            }
                        ],
                    ),
                }
            },
            deque(["Resources", "TaskDefinition", "Properties"]),
            [
                ValidationError(
                    ("'80' does not equal 8080"),
                    validator="const",
                    rule=TaskDefinitionAwsVpc(),
                    path_override=deque(
                        [
                            "Resources",
                            "TaskDefinition",
                            "Properties",
                            "ContainerDefinitions",
                            0,
                            "PortMappings",
                            0,
                            "HostPort",
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
