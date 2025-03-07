"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class PipelineFirstStageHasSource(CfnLintKeyword):
    id = "E3700"
    shortdesc = "Validate CodePipeline Source actions are only in the first stage"
    description = (
        "When using AWS::CodePipeline::Pipeline this rule will validate "
        "that Source actions are only used in the first stage"
    )
    tags = ["resources", "codepipeline"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::CodePipeline::Pipeline/Properties/Stages/*/Actions/*/ActionTypeId/Category"
            ],
        )
        self._valid_categories = [
            # removed because Source is only in the first stage
            # "Source",
            "Build",
            "Approval",
            "Deploy",
            "Test",
            "Invoke",
            "Compute",
        ]

    def _is_first_stage(self, full_path: deque) -> bool | None:
        path = list(full_path)[3:]
        i = path.index("Stages")
        while i < len(path):
            if path[i] == "Fn::If":
                i += 2
                continue
            if path[i] == 0:
                return True
            elif isinstance(path[i], int):
                return False
            i += 1

        return None

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        is_first_stage = self._is_first_stage(validator.context.path.path)
        if is_first_stage is None:
            return
        if is_first_stage:
            if instance != "Source":
                yield ValidationError(
                    f"{instance!r} is not one of {['Source']!r}",
                    rule=self,
                    validator="enum",
                )
        else:
            if instance not in self._valid_categories:
                yield ValidationError(
                    f"{instance!r} is not one of {self._valid_categories!r}",
                    rule=self,
                    validator="enum",
                )
