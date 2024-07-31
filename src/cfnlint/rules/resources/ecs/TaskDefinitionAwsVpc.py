"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

from cfnlint.jsonschema import ValidationError, ValidationResult
from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class TaskDefinitionAwsVpc(CfnLintKeyword):
    id = "E3053"
    shortdesc = "Validate ECS task definition is has correct values for 'HostPort'"
    description = (
        "The 'HostPort' must either be undefined or equal to "
        "the 'ContainerPort' value"
    )
    tags = ["resources", "ecs"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::TaskDefinition/Properties"],
        )

    def _get_port_mappings(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[str | int | None, str | int | None, Validator]]:

        for container_definition, container_definition_validator in get_value_from_path(
            validator,
            instance,
            path=deque(["ContainerDefinitions", "*", "PortMappings", "*"]),
        ):
            for host_port, host_port_validator in get_value_from_path(
                container_definition_validator,
                container_definition,
                path=deque(["HostPort"]),
            ):
                if not isinstance(host_port, (str, int)):
                    continue
                for container_port, _ in get_value_from_path(
                    host_port_validator,
                    container_definition,
                    path=deque(["ContainerPort"]),
                ):
                    if not isinstance(container_port, (str, int)):
                        continue
                    if str(host_port) != str(container_port):
                        yield host_port, container_port, host_port_validator

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for network_mode, _ in get_value_from_path(
            validator,
            instance,
            path=deque(["NetworkMode"]),
        ):
            if network_mode != "awsvpc":
                continue
            for (
                host_port,
                container_port,
                port_mapping_validator,
            ) in self._get_port_mappings(
                validator,
                instance,
            ):
                yield ValidationError(
                    f"{host_port!r} does not equal {container_port!r}",
                    validator="const",
                    rule=self,
                    path_override=port_mapping_validator.context.path.path,
                )
