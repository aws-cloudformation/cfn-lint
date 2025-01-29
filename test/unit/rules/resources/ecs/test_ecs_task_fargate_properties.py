"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ecs.TaskFargateProperties import TaskFargateProperties


@pytest.fixture(scope="module")
def rule():
    rule = TaskFargateProperties()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 256,
                "Memory": "512",
            },
            [],
        ),
        (
            {
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": ".25     vCpU",
                "Memory": "512",
            },
            [],
        ),
        (
            {
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 16384,
            },
            [
                ValidationError(
                    "'Memory' is a required property",
                    rule=TaskFargateProperties(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "allOf", 2, "required"]),
                )
            ],
        ),
        (
            {
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Memory": "512",
            },
            [
                ValidationError(
                    "'Cpu' is a required property",
                    rule=TaskFargateProperties(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "allOf", 2, "required"]),
                )
            ],
        ),
        (
            {
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Memory": "512",
                "Cpu": 256,
                "PlacementConstraints": "foo",
            },
            [
                ValidationError(
                    ("'PlacementConstraints' isn't supported for Fargate tasks"),
                    rule=TaskFargateProperties(),
                    path=deque(["PlacementConstraints"]),
                    validator="not",
                    schema_path=deque(["then", "allOf", 2, "not"]),
                )
            ],
        ),
        (
            {
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": {"Ref": "MyParameter"},
                "Memory": "512",
            },
            [],
        ),
        (
            {
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 128,
                "Memory": "512",
            },
            [
                ValidationError(
                    (
                        "128 is not one of ['256', '512', '1024', '2048', "
                        "'4096', '8192', '16384']"
                    ),
                    rule=TaskFargateProperties(),
                    path=deque(["Cpu"]),
                    validator="enum",
                    schema_path=deque(
                        [
                            "then",
                            "allOf",
                            2,
                            "then",
                            "properties",
                            "Cpu",
                            "then",
                            "enum",
                        ]
                    ),
                )
            ],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 256,
                "Memory": "512",
                "NetworkMode": {"Ref": "MyParameter"},
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 256,
                "Memory": "512",
            },
            [
                ValidationError(
                    ("'NetworkMode' is a required property"),
                    rule=TaskFargateProperties(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "allOf", 0, "required"]),
                )
            ],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 256,
                "Memory": "512",
                "NetworkMode": "awsvpc",
                "ContainerDefinitions": [
                    {
                        "LogConfiguration": {
                            "LogDriver": "awslogs",
                            "Options": {
                                "awslogs-group": "log-group",
                                "awslogs-region": "us-east-1",
                                "awslogs-stream-prefix": "ecs",
                            },
                        }
                    }
                ],
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 256,
                "Memory": "512",
                "NetworkMode": "awsvpc",
                "ContainerDefinitions": [
                    {
                        "LogConfiguration": {
                            "LogDriver": {"Ref": "MyParameter"},
                            "Options": {
                                "awslogs-group": "log-group",
                                "awslogs-region": "us-east-1",
                                "awslogs-stream-prefix": "ecs",
                            },
                        }
                    }
                ],
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 256,
                "Memory": "512",
                "NetworkMode": "awsvpc",
                "ContainerDefinitions": [
                    {
                        "LogConfiguration": {
                            "LogDriver": "sumologic",
                            "Options": {
                                "sumo-url": "aurl",
                                "sumo-source-category": "access",
                            },
                        }
                    }
                ],
            },
            [
                ValidationError(
                    ("'sumologic' is not one of ['awslogs', 'splunk', 'awsfirelens']"),
                    rule=TaskFargateProperties(),
                    path=deque(
                        ["ContainerDefinitions", 0, "LogConfiguration", "LogDriver"]
                    ),
                    validator="enum",
                    schema_path=deque(
                        [
                            "then",
                            "allOf",
                            1,
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
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
