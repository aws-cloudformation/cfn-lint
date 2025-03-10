"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.context.conditions import Unsatisfiable
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class PipelineArtifactNames(CfnLintKeyword):
    id = "E3701"
    shortdesc = "Validate input and output artifact names are used properly"
    description = (
        "When using AWS::CodePipeline::Pipeline InputArtifacts names "
        "have to be previously used OutputArtifact names. Additionally, "
        "the OutputArtifacts names have to be unique"
    )
    tags = ["resources", "codepipeline"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::CodePipeline::Pipeline/Properties/Stages/*/Actions/*/InputArtifacts/*/Name",
                "Resources/AWS::CodePipeline::Pipeline/Properties/Stages/*/Actions/*/OutputArtifacts/*/Name",
            ],
        )
        self._output_artifact_names: dict[str, list[tuple[str, dict]]] = {}

    def initialize(self, cfn):
        self._output_artifact_names = {}
        return super().initialize(cfn)

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        resource_name = validator.context.path.path[1]
        if not isinstance(resource_name, str):
            return

        if resource_name not in self._output_artifact_names:
            self._output_artifact_names[resource_name] = []

        if "OutputArtifacts" in validator.context.path.path:
            for output_name, output_condition in self._output_artifact_names[
                resource_name
            ]:
                if output_name != instance:
                    continue
                try:
                    validator.evolve(
                        context=validator.context.evolve(
                            conditions=validator.context.conditions.evolve(
                                output_condition
                            )
                        )
                    )
                    yield ValidationError(
                        f"{instance!r} is already a defined 'OutputArtifact' Name",
                        rule=self,
                    )
                    return
                except Unsatisfiable:
                    pass

            self._output_artifact_names[resource_name].append(
                (instance, validator.context.conditions.status)
            )
        elif "InputArtifacts" in validator.context.path.path:
            for output_name, output_condition in self._output_artifact_names[
                resource_name
            ]:
                if output_name != instance:
                    continue
                try:
                    validator.evolve(
                        context=validator.context.evolve(
                            conditions=validator.context.conditions.evolve(
                                output_condition
                            )
                        )
                    )
                    break
                except Unsatisfiable:
                    pass
            else:
                yield ValidationError(
                    f"{instance!r} is not previously defined as an 'OutputArtifact'",
                    rule=self,
                )
                return
