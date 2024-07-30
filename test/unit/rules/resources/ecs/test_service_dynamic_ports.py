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
from cfnlint.rules.resources.ecs.ServiceDynamicPorts import ServiceDynamicPorts


@pytest.fixture
def rule():
    rule = ServiceDynamicPorts()
    yield rule


_task_definition = {
    "Type": "AWS::ECS::TaskDefinition",
    "Properties": {
        "ContainerDefinitions": [
            {
                "Name": "my-container",
                "Image": "my-image",
                "PortMappings": [
                    {
                        "ContainerPort": 8080,
                        "HostPort": 0,
                    }
                ],
            }
        ],
    },
}

_target_group = {
    "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
    "Properties": {
        "HealthCheckPort": "traffic-port",
        "Port": 8080,
        "Protocol": "HTTP",
    },
}

_service = {
    "Type": "AWS::ECS::Service",
    "Properties": {
        "TaskDefinition": {"Ref": "TaskDefinition"},
        "LoadBalancers": [
            {
                "TargetGroupArn": {"Ref": "TargetGroup"},
                "ContainerName": "my-container",
                "ContainerPort": 8080,
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
                    "TargetGroup": dict(_target_group),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [],
        ),
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
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": "3000",
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
                "Parameters": {
                    "MyHealthCheckPort": {
                        "Type": "String",
                    },
                },
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": {"Ref": "MyHealthCheckPort"},
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
                "Parameters": {
                    "MyContainerPort": {
                        "Type": "String",
                    },
                },
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": (
                                    "/Properties/ContainerDefinitions"
                                    "/0/PortMappings/0/ContainerPort"
                                ),
                                "value": {"Ref": "MyContainerPort"},
                            },
                        ],
                    ),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": "3000",
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
                "Parameters": {
                    "MyTaskDefinition": {
                        "Type": "String",
                    },
                },
                "Resources": {
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": "3000",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Ref": "MyTaskDefinition"},
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
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": "3000",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Fn::FindInMap": ["A", "B", "C"]},
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
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": "3000",
                            },
                        ],
                    ),
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
            [
                ValidationError(
                    (
                        "When using an ECS task definition of host "
                        "port 0 and associating that container to "
                        "an ELB the target group has to have a "
                        "'HealthCheckPort' of 'traffic-port'"
                    ),
                    validator="const",
                    path_override=deque(
                        ["Resources", "TargetGroup", "Properties", "HealthCheckPort"]
                    ),
                    rule=ServiceDynamicPorts(),
                )
            ],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": "3000",
                            },
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/TaskDefinition",
                                "value": {"Ref": []},
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
                    "TaskDefinition": dict(_task_definition),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/HealthCheckPort",
                                "value": "3000",
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
                        "When using an ECS task definition of host "
                        "port 0 and associating that container to "
                        "an ELB the target group has to have a "
                        "'HealthCheckPort' of 'traffic-port'"
                    ),
                    validator="const",
                    path_override=deque(
                        ["Resources", "TargetGroup", "Properties", "HealthCheckPort"]
                    ),
                    rule=ServiceDynamicPorts(),
                )
            ],
        ),
        (
            {
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
                        ],
                    ),
                    "Service": dict(_service),
                }
            },
            deque(["Resources", "Service", "Properties"]),
            [
                ValidationError(
                    (
                        "When using an ECS task definition of host "
                        "port 0 and associating that container to "
                        "an ELB the target group has to have a "
                        "'HealthCheckPort' of 'traffic-port'"
                    ),
                    validator="required",
                    path_override=deque(
                        ["Resources", "TargetGroup", "Properties", "HealthCheckPort"]
                    ),
                    rule=ServiceDynamicPorts(),
                )
            ],
        ),
        (
            {
                "Parameters": {
                    "MyContainerName": {
                        "Type": "String",
                    }
                },
                "Resources": {
                    "TaskDefinition": jsonpatch.apply_patch(
                        dict(_task_definition),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/ContainerDefinitions/0/Name",
                                "value": {"Ref": "MyContainerName"},
                            },
                        ],
                    ),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
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
                "Parameters": {
                    "MyContainerName": {
                        "Type": "String",
                    }
                },
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "replace",
                                "path": "/Properties/LoadBalancers/0/ContainerName",
                                "value": {"Ref": "MyContainerName"},
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
                "Parameters": {
                    "MyContainerName": {
                        "Type": "String",
                    }
                },
                "Resources": {
                    "TaskDefinition": dict(_task_definition),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/LoadBalancers/0/ContainerName",
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
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/LoadBalancers/0/ContainerPort",
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
                    "TaskDefinition": dict(_task_definition),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
                        ],
                    ),
                    "Service": jsonpatch.apply_patch(
                        dict(_service),
                        [
                            {
                                "op": "remove",
                                "path": "/Properties/LoadBalancers/0/TargetGroupArn",
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
                                "path": "/Properties/ContainerDefinitions/0/Name",
                                "value": "Changed",
                            },
                        ],
                    ),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
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
                                "path": (
                                    "/Properties/ContainerDefinitions/"
                                    "0/PortMappings/0/ContainerPort"
                                ),
                                "value": "30",
                            },
                        ],
                    ),
                    "TargetGroup": jsonpatch.apply_patch(
                        dict(_target_group),
                        [
                            {"op": "remove", "path": "/Properties/HealthCheckPort"},
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
                                "path": (
                                    "/Properties/ContainerDefinitions/"
                                    "0/PortMappings/0/HostPort"
                                ),
                                "value": "30",
                            },
                        ],
                    ),
                    "TargetGroup": dict(_target_group),
                    "Service": dict(_service),
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
