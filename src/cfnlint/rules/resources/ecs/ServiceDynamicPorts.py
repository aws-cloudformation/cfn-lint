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

    def _filter_resource_name(self, instance: Any) -> str | None:
        fn_k, fn_v = is_function(instance)
        if fn_k is None:
            return None
        if fn_k == "Ref":
            if isinstance(fn_v, str):
                return fn_v
        elif fn_k == "Fn::GetAtt":
            name = ensure_list(fn_v)[0].split(".")[0]
            if isinstance(name, str):
                return name
        return None

    def _get_service_lb_containers(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[str, str, str, Validator]]:
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
                if name is None or not isinstance(name, str):
                    continue
                for port, port_validator in get_value_from_path(
                    name_validator,
                    load_balancer,
                    path=deque(["ContainerPort"]),
                ):
                    if port is None or not isinstance(port, (str, int)):
                        continue
                    for tg, tg_validator in get_value_from_path(
                        port_validator,
                        load_balancer,
                        path=deque(["TargetGroupArn"]),
                    ):
                        tg = self._filter_resource_name(tg)
                        if tg is None:
                            continue
                        yield name, port, tg, tg_validator

    def _get_service_properties(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[str, str, str, str, Validator]]:
        for task_definition_id, task_definition_validator in get_value_from_path(
            validator, instance, deque(["TaskDefinition"])
        ):
            task_definition_resource_name = self._filter_resource_name(
                task_definition_id
            )
            if task_definition_resource_name is None:
                continue
            for (
                container_name,
                container_port,
                target_group,
                lb_validator,
            ) in self._get_service_lb_containers(task_definition_validator, instance):
                yield (
                    task_definition_resource_name,
                    container_name,
                    container_port,
                    target_group,
                    lb_validator,
                )

    def _get_target_group_properties(
        self, validator: Validator, resource_name: Any
    ) -> Iterator[tuple[str | int | None, Validator]]:
        target_group, target_group_validator = get_resource_by_name(
            validator, resource_name, ["AWS::ElasticLoadBalancingV2::TargetGroup"]
        )
        if not target_group:
            return

        for port, port_validator in get_value_from_path(
            target_group_validator,
            target_group,
            path=deque(["Properties", "HealthCheckPort"]),
        ):
            if port is None:
                yield port, port_validator
                continue

            if not isinstance(port, (str, int)):
                continue
            yield port, port_validator

    def _get_task_containers(
        self,
        validator: Validator,
        resource_name: str,
        container_name: str,
        container_port: str | int,
    ) -> Iterator[Validator]:
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
                    for host_port_validator in self._filter_port_mappings(
                        name_validator, container, container_port
                    ):
                        yield host_port_validator

    def _filter_port_mappings(
        self, validator: Validator, instance: Any, port: Any
    ) -> Iterator[Validator]:
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
                        if str(host_port) == "0":
                            yield host_part_validator

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for (
            task_definition_resource_name,
            lb_container_name,
            lb_container_port,
            lb_target_group,
            lb_service_validator,
        ) in self._get_service_properties(validator, instance):
            for container_validator in self._get_task_containers(
                lb_service_validator,
                task_definition_resource_name,
                lb_container_name,
                lb_container_port,
            ):
                for (
                    health_check_port,
                    health_check_port_validator,
                ) in self._get_target_group_properties(
                    container_validator, lb_target_group
                ):
                    if health_check_port != "traffic-port":
                        err_validator = "const"
                        if health_check_port is None:
                            err_validator = "required"
                        yield ValidationError(
                            "When using an ECS task definition of host port 0 and "
                            "associating that container to an ELB the target group "
                            "has to have a 'HealthCheckPort' of 'traffic-port'",
                            path_override=health_check_port_validator.context.path.path,
                            validator=err_validator,
                            rule=self,
                        )
