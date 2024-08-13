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


class ServiceFargate(CfnLintKeyword):
    id = "E3054"
    shortdesc = (
        "Validate ECS service using Fargate uses TaskDefinition that allows Fargate"
    )
    description = (
        "When using an ECS service with 'LaunchType' of 'FARGATE' "
        "the associated task definition must have 'RequiresCompatibilities' "
        "specified with 'FARGATE' listed"
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
                launch_type,
                launch_type_validator,
            ) in get_value_from_path(
                task_definition_validator, instance, deque(["LaunchType"])
            ):
                yield (
                    task_definition_resource_name,
                    launch_type,
                    launch_type_validator,
                )

    def _get_task_definition_properties(
        self, validator: Validator, resource_name: Any
    ) -> Iterator[tuple[list[Any] | None, Validator]]:
        task_definition, task_definition_validator = get_resource_by_name(
            validator, resource_name, ["AWS::ECS::TaskDefinition"]
        )
        if not task_definition:
            return
        for capabilities, capabilities_validator in get_value_from_path(
            task_definition_validator,
            task_definition,
            path=deque(["Properties", "RequiresCompatibilities"]),
        ):
            for network_mode, network_mode_validator in get_value_from_path(
                capabilities_validator,
                task_definition,
                path=deque(["Properties", "NetworkMode"]),
            ):

                if network_mode == "awsvpc" or network_mode_validator.is_type(
                    network_mode, "object"
                ):
                    continue
                if capabilities is None:
                    yield capabilities, capabilities_validator
                    continue
                if not isinstance(capabilities, list):
                    continue
                for capibility, _ in get_value_from_path(
                    network_mode_validator,
                    capabilities,
                    path=deque(["*"]),
                ):
                    if isinstance(capibility, dict) or capibility == "FARGATE":
                        break
                else:
                    yield capabilities, capabilities_validator

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for (
            task_definition_resource_name,
            launch_type,
            service_validator,
        ) in self._get_service_properties(
            validator,
            instance,
        ):
            if launch_type != "FARGATE":
                continue
            for (
                capabilities,
                capabilities_validator,
            ) in self._get_task_definition_properties(
                service_validator,
                task_definition_resource_name,
            ):
                if capabilities is None:
                    yield ValidationError(
                        "'RequiresCompatibilities' is a required property",
                        validator="required",
                        rule=self,
                        path_override=deque(
                            list(capabilities_validator.context.path.path)[:-1]
                        ),
                    )
                    continue

                yield ValidationError(
                    f"{capabilities!r} does not contain items matching 'FARGATE'",
                    validator="contains",
                    rule=self,
                    path_override=capabilities_validator.context.path.path,
                )
