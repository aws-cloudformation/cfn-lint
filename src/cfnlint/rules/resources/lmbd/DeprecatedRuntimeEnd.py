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


class DeprecatedRuntimeEnd(CfnLintKeyword):

    id = "E2531"
    shortdesc = "Validate if lambda runtime is deprecated"
    description = "Check the lambda runtime has reached the end of life"
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html"
    tags = ["resources", "lambda", "runtime"]

    def __init__(self):
        """Init"""
        super().__init__(["Resources/AWS::Lambda::Function/Properties/Runtime"])
        self.child_rules = {
            "W2531": None,
        }
        self.current_date = datetime.today()
        self.deprecated_runtimes = load_resource(
            AdditionalSpecs, "LmbdRuntimeLifecycle.json"
        )

    # pylint: disable=unused-argument
    def validate(
        self, validator: Validator, v: Any, runtime: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        runtime_data = self.deprecated_runtimes.get(runtime)
        if not runtime_data:
            return
        if (
            datetime.strptime(runtime_data["deprecated"], "%Y-%m-%d")
            < self.current_date
        ):
            yield ValidationError(
                (
                    f"Deprecated runtime {runtime!r} specified. Updating "
                    f"disabled since {runtime_data['deprecated']!r}. "
                    f"Please consider updating to {runtime_data['successor']!r}"
                ),
                rule=self,
            )

        if self.child_rules["W2531"]:
            yield from self.child_rules["W2531"].lambdaruntime(runtime, runtime_data)  # type: ignore
