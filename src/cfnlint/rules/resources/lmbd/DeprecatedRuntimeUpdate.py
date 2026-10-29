"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cfnlint.data import AdditionalSpecs
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword
from cfnlint.rules.resources.lmbd._runtime_lifecycle import deprecated_message


class DeprecatedRuntimeUpdate(CfnLintKeyword):
    id = "E2533"
    shortdesc = "Check if Lambda Function Runtimes are updatable"
    description = (
        "Check if an EOL Lambda Runtime is specified and you cannot update the function"
    )
    source_url = (
        "https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html"
    )
    tags = ["resources", "lambda", "runtime"]

    def __init__(self):
        """Init"""
        super().__init__(
            [
                "Resources/AWS::Lambda::Function/Properties/Runtime",
                "Resources/AWS::Serverless::Function/Properties/Runtime",
                "Globals/Function/Runtime",
            ]
        )
        self.deprecated_runtimes = load_resource(
            AdditionalSpecs, "LmbdRuntimeLifecycle.json"
        )

    def validate(
        self, validator: Validator, v: Any, runtime: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(runtime, "string"):
            return
        runtime_data = self.deprecated_runtimes.get(runtime)
        if not runtime_data:
            return
        current_date = datetime.today()
        update_block = runtime_data["update-block"]

        if update_block is None:
            return

        if datetime.strptime(update_block, "%Y-%m-%d") <= current_date:
            yield ValidationError(deprecated_message(runtime, runtime_data))
