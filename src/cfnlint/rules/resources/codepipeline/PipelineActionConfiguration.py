"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class PipelineActionConfiguration(CfnLintKeyword):
    id = "E3703"
    shortdesc = "Validate the configuration of a pipeline action"
    description = (
        "When definition a CodePipeline certain action types have "
        "configuration constraints so this rule validates them"
    )
    tags = ["resources", "codepipeline"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::CodePipeline::Pipeline/Properties/Stages/*/Actions/*",
            ],
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        for template_path, template_path_validator in get_value_from_path(
            validator, instance, path=deque(["Configuration", "TemplatePath"])
        ):
            if not validator.is_type(template_path, "string"):
                continue
            input_artficat_names = set()
            for input_name, _ in get_value_from_path(
                template_path_validator,
                instance,
                path=deque(["InputArtifacts", "*", "Name"]),
            ):
                if not validator.is_type(input_name, "string"):
                    continue
                if template_path.startswith(f"{input_name}::"):
                    break
                input_artficat_names.add(input_name)
            else:
                yield ValidationError(
                    (
                        f"{template_path.split('::')[0]!r} is not "
                        f"one of {list(input_artficat_names)!r}"
                    ),
                    validator="enum",
                    rule=self,
                    path_override=template_path_validator.context.path.path,
                )

        for role, role_validator in get_value_from_path(
            validator, instance, path=deque(["Configuration", "RoleArn"])
        ):
            if role is None:
                continue
            role_validator = role_validator.evolve(
                schema={"format": "AWS::IAM::Role.Arn"}
            )

            for err in role_validator.iter_errors(role):
                err.rule = self
                err.path_override = role_validator.context.path.path
                yield err
