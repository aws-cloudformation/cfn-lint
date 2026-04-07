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
from cfnlint.rules.resources.ecs.ServiceFargateLogDriver import ServiceFargateLogDriver

_LOG_DRIVER_PATH = "/Properties/ContainerDefinitions/0/LogConfiguration/LogDriver"
_LOG_CONFIG_PATH = "/Properties/ContainerDefinitions/0/LogConfiguration"


@pytest.fixture
def rule():
    rule = ServiceFargateLogDriver()
    yield rule


_task_definition = {
    "Type": "AWS::ECS::TaskDefinition",
    "Properties": {
        "RequiresCompatibilities": ["FARGATE"],
        "ContainerDefinitions": [
            {
                "Name": "app",
                "Image": "my-image:latest",
                "LogConfiguration": {
                    "LogDriver": "awslogs",
                    "Options": {
                        "awslogs-group": "/ecs/app",
                        "awslogs-region": "us-east-1",
                    },
                },
            }
        ],
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
        # Valid: awslogs driver with Fargate
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
        # Valid: splunk driver with Fargate
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": _LOG_DRIVER_PATH,
                                "value": "splunk",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        # Valid: awsfirelens driver with Fargate
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": _LOG_DRIVER_PATH,
                                "value": "awsfirelens",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        # Valid: EC2 launch type with json-file driver (no restriction)
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": _LOG_DRIVER_PATH,
                                "value": "json-file",
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
        # Valid: no LogConfiguration specified
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "remove",
                                "path": _LOG_CONFIG_PATH,
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        # Valid: TaskDefinition is a parameter reference (can't validate)
        (
            {
                "Parameters": {"MyTask": {"Type": "String"}},
                "Resources": {
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
        # Valid: TaskDefinition is a hardcoded ARN (can't validate)
        (
            {
                "Resources": {
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": "arn:aws:ecs:us-east-1:0:task/t:1",
                            },
                        ],
                    ),
                },
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
        # Invalid: json-file driver with Fargate
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": _LOG_DRIVER_PATH,
                                "value": "json-file",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    (
                        "'json-file' is not a supported Fargate log driver. "
                        "Use 'awslogs', 'splunk', or 'awsfirelens'"
                    ),
                    validator="enum",
                    rule=ServiceFargateLogDriver(),
                    path_override=deque(
                        [
                            "Resources",
                            "TaskDefinition",
                            "Properties",
                            "ContainerDefinitions",
                            0,
                            "LogConfiguration",
                            "LogDriver",
                        ]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "taskDef",
                            "properties",
                            "ContainerDefinitions",
                            "items",
                            "properties",
                            "LogConfiguration",
                            "then",
                            "properties",
                            "LogDriver",
                            "enum",
                        ]
                    ),
                )
            ],
        ),
        # Invalid: syslog driver with Fargate
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": _LOG_DRIVER_PATH,
                                "value": "syslog",
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    (
                        "'syslog' is not a supported Fargate log driver. "
                        "Use 'awslogs', 'splunk', or 'awsfirelens'"
                    ),
                    validator="enum",
                    rule=ServiceFargateLogDriver(),
                    path_override=deque(
                        [
                            "Resources",
                            "TaskDefinition",
                            "Properties",
                            "ContainerDefinitions",
                            0,
                            "LogConfiguration",
                            "LogDriver",
                        ]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "taskDef",
                            "properties",
                            "ContainerDefinitions",
                            "items",
                            "properties",
                            "LogConfiguration",
                            "then",
                            "properties",
                            "LogDriver",
                            "enum",
                        ]
                    ),
                )
            ],
        ),
        # Invalid: multiple containers, one with bad driver
        (
            {
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "add",
                                "path": "/Properties/ContainerDefinitions/1",
                                "value": {
                                    "Name": "sidecar",
                                    "Image": "sidecar:latest",
                                    "LogConfiguration": {
                                        "LogDriver": "fluentd",
                                    },
                                },
                            },
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    (
                        "'fluentd' is not a supported Fargate log driver. "
                        "Use 'awslogs', 'splunk', or 'awsfirelens'"
                    ),
                    validator="enum",
                    rule=ServiceFargateLogDriver(),
                    path_override=deque(
                        [
                            "Resources",
                            "TaskDefinition",
                            "Properties",
                            "ContainerDefinitions",
                            1,
                            "LogConfiguration",
                            "LogDriver",
                        ]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "taskDef",
                            "properties",
                            "ContainerDefinitions",
                            "items",
                            "properties",
                            "LogConfiguration",
                            "then",
                            "properties",
                            "LogDriver",
                            "enum",
                        ]
                    ),
                )
            ],
        ),
        # Valid: Fn::GetAtt reference to TaskDefinition with valid driver
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Fn::GetAtt": ["TaskDefinition", "Arn"]},
                            },
                        ],
                    ),
                }
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
