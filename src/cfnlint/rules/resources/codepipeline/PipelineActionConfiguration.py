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
    shortdesc = "RestApi requires a name when not using an OpenAPI specification"
    description = (
        "When using AWS::ApiGateway::RestApi you have to provide 'Name' "
        "if you don't provide 'Body' or 'BodyS3Location'"
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
