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


class ServiceNetworkConfiguration(CfnLintKeyword):
    id = "E3052"
    shortdesc = "Validate ECS service requires NetworkConfiguration"
    description = (
        "When using an ECS task definition has NetworkMode set to "
        "'awsvpc' then 'NetworkConfiguration' is required"
    )
    tags = ["resources", "ecs"]

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

    def _get_service_properties(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[str, str, Validator]]:
        for task_definition_id, task_definition_validator in get_value_from_path(
            validator, instance, deque(["TaskDefinition"])
        ):
            task_definition_resource_name = self._filter_resource_name(
                task_definition_id
            )
            if task_definition_resource_name is None:
                continue

            for (
                network_configuration,
                network_configuration_validator,
            ) in get_value_from_path(
                task_definition_validator, instance, deque(["NetworkConfiguration"])
            ):
                yield (
                    task_definition_resource_name,
                    network_configuration,
                    network_configuration_validator,
                )

    def _get_task_definition_properties(
        self, validator: Validator, resource_name: Any
    ) -> Iterator[tuple[str | int | None, Validator]]:
        target_group, target_group_validator = get_resource_by_name(
            validator, resource_name, ["AWS::ECS::TaskDefinition"]
        )
        if not target_group:
            return

        for network_mode, network_mode_validator in get_value_from_path(
            target_group_validator,
            target_group,
            path=deque(["Properties", "NetworkMode"]),
        ):
            if network_mode == "awsvpc":
                yield network_mode, network_mode_validator

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for (
            task_definition_resource_name,
            network_configuration,
            task_definition_validator,
        ) in self._get_service_properties(
            validator,
            instance,
        ):
            for _, _ in self._get_task_definition_properties(
                task_definition_validator,
                task_definition_resource_name,
            ):
                if network_configuration is None:
                    yield ValidationError(
                        "'NetworkConfiguration' is a required property",
                        validator="required",
                        rule=self,
                    )
