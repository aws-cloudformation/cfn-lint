"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class SnapStartSupported(CfnLintKeyword):
    """Check if Lambda function using SnapStart has the correct runtimes"""

    id = "E2530"
    shortdesc = "SnapStart supports the configured runtime"
    description = (
        "To properly leverage SnapStart, you must have a runtime of Java11 or greater"
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html"
    tags = ["resources", "lambda"]

    def __init__(self):
        super().__init__(["Resources/AWS::Lambda::Function/Properties"])
        self.child_rules = {"I2530": None}
        self.regions = [
            "us-east-2",
            "us-east-1",
            "us-west-1",
            "us-west-2",
            "af-south-1",
            "ap-east-1",
            "ap-southeast-3",
            "ap-south-1",
            "ap-northeast-2",
            "ap-northeast-3",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
            "ca-central-1",
            "eu-central-1",
            "eu-west-1",
            "eu-west-2",
            "eu-south-1",
            "eu-west-3",
            "eu-north-1",
            "me-south-1",
            "sa-east-1",
        ]

    def _is_runtime_valid(self, runtime: str) -> bool:
        if not any(runtime.startswith(r) for r in ["python", "java", "dotnet"]):
            return False

        if runtime.startswith("dotnetcore"):
            return False

        return runtime not in [
            "dotnet5.0",
            "dotnet6",
            "dotnet7",
            "java8.al2",
            "java8",
            "python3.10",
            "python3.11",
            "python3.7",
            "python3.8",
            "python3.9",
        ]

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for scenario in validator.cfn.get_object_without_conditions(
            instance,
            ["Runtime", "SnapStart"],
        ):
            props = scenario.get("Object")

            runtime = props.get("Runtime")
            snap_start = props.get("SnapStart")
            if not snap_start:
                if self.child_rules["I2530"]:
                    if all(
                        region in self.regions for region in validator.context.regions
                    ):
                        yield from self.child_rules["I2530"].validate(  # type: ignore
                            runtime,
                        )
                continue

            if snap_start.get("ApplyOn") != "PublishedVersions":
                continue

            if any(region not in self.regions for region in validator.context.regions):
                unsupported_regions = [
                    region
                    for region in validator.context.regions
                    if region not in self.regions
                ]
                yield ValidationError(
                    (
                        "'SnapStart' enabled functions are not supported in "
                        f"{unsupported_regions!r}"
                    ),
                    path=deque(["SnapStart", "ApplyOn"]),
                )

            # Validate runtime is a string before using startswith
            if not isinstance(runtime, str):
                continue

            if not self._is_runtime_valid(runtime):
                yield ValidationError(
                    f"{runtime!r} is not supported for 'SnapStart' enabled functions",
                    path=deque(["SnapStart", "ApplyOn"]),
                )
