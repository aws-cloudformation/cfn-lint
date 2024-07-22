"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

from cfnlint.helpers import ensure_list, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult
from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules.helpers import get_resource_by_name, get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class ServiceDynamicPorts(CfnLintKeyword):
    id = "E3049"
    shortdesc = (
        "Validate ECS tasks with dynamic host port have traffic-port ELB target groups"
    )
    description = (
        "When using an ECS task definition of host port 0 and "
        "associating that container to an ELB the target group "
        "has to have a 'HealthCheckPort' of 'traffic-port'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::Service/Properties"],
        )

    def _get_service_lb_containers(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[str, str, Validator]]:

        for load_balancer, load_balancer_validator in get_value_from_path(
            validator,
            instance,
            path=deque(["LoadBalancers", "*"]),
        ):
            for name, name_validator in get_value_from_path(
                load_balancer_validator,
                load_balancer,
                path=deque(["ContainerName"]),
            ):
                if name is None:
                    continue
                for port, port_validator in get_value_from_path(
                    name_validator,
                    load_balancer,
                    path=deque(["ContainerPort"]),
                ):
                    if port is None:
                        continue
                    yield name, port, port_validator

    def _get_task_definition_resource_name(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[str, Validator]]:
        for task_definition_id, task_definition_validator in get_value_from_path(
            validator, instance, deque(["TaskDefinition"])
        ):
            fn_k, fn_v = is_function(task_definition_id)
            if fn_k == "Ref":
                if validator.is_type(fn_v, "string"):
                    if fn_v in validator.context.resources:
                        yield fn_v, task_definition_validator
            elif fn_k != "Fn::GetAtt":
                continue
            yield ensure_list(fn_v)[0].split(".")[0], task_definition_validator

    def _get_task_containers(
        self, validator: Validator, resource_name: str, container_name: str
    ) -> Iterator[tuple[Any, Validator]]:
        task_def, task_def_validator = get_resource_by_name(
            validator, resource_name, ["AWS::ECS::TaskDefinition"]
        )

        if not task_def:
            return

        for container, container_validator in get_value_from_path(
            task_def_validator,
            task_def,
            path=deque(["Properties", "ContainerDefinitions", "*"]),
        ):
            for name, name_validator in get_value_from_path(
                container_validator,
                container,
                path=deque(["Name"]),
            ):
                if not isinstance(name, str):
                    continue
                if name == container_name:
                    yield container, name_validator

    def _filter_port_mappings(
        self, validator: Validator, instance: Any, port: Any
    ) -> Iterator[tuple[Any, Validator]]:
        for port_mapping, port_mapping_validator in get_value_from_path(
            validator,
            instance,
            path=deque(["PortMappings", "*"]),
        ):
            for container_port, container_port_validator in get_value_from_path(
                port_mapping_validator,
                port_mapping,
                path=deque(["ContainerPort"]),
            ):
                if not isinstance(container_port, (str, int)):
                    continue
                if str(port) == str(container_port):
                    for host_port, host_part_validator in get_value_from_path(
                        container_port_validator,
                        port_mapping,
                        path=deque(["HostPort"]),
                    ):
                        yield host_port, host_part_validator

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for (
            task_definition_resource_name,
            task_definition_resource_name_validator,
        ) in self._get_task_definition_resource_name(validator, instance):

            for name, port, lb_validator in self._get_service_lb_containers(
                task_definition_resource_name_validator, instance
            ):
                for container, container_validator in self._get_task_containers(
                    lb_validator, task_definition_resource_name, name
                ):
                    for host_port, host_port_validator in self._filter_port_mappings(
                        container_validator, container, port
                    ):
                        if host_port == 0:
                            yield ValidationError(
                                "When using an ECS task definition of host port 0 and "
                                "associating that container to an ELB the target group "
                                "has to have a 'HealthCheckPort' of 'traffic-port'",
                            )

        return
        yield
