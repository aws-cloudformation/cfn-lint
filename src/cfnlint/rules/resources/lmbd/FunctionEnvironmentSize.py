"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class FunctionEnvironmentSize(CfnLintKeyword):
    """Check Lambda environment variables total size does not exceed 4 KB"""

    id = "E3697"
    shortdesc = "Validate Lambda environment variables do not exceed 4 KB"
    description = (
        "AWS Lambda limits the total size of all environment variables "
        "to 4 KB. If this limit is exceeded, the deployment will fail. "
        "This rule sums the lengths of all keys and values and validates "
        "the total does not exceed 4096 bytes."
    )
    source_url = (
        "https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html"
    )
    tags = ["resources", "lambda"]

    def __init__(self):
        """Init"""
        super().__init__(
            ["Resources/AWS::Lambda::Function/Properties/Environment/Variables"]
        )

    def validate(
        self,
        validator: Validator,
        keywords: Any,
        instance: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        total_size = 0
        for key, value in instance.items():
            if not isinstance(key, str):
                continue
            total_size += len(key.encode("utf-8"))
            total_size += self._max_value_size(validator, value)

        max_size = 4096
        if total_size > max_size:
            yield ValidationError(
                f"Lambda environment variables total size ({total_size}) "
                f"exceeds the 4 KB ({max_size} bytes) limit",
                rule=self,
            )

    def _max_value_size(self, validator: Validator, value: Any) -> int:
        """Return the largest UTF-8 byte size across resolvable value scenarios.

        Intrinsic functions such as Fn::Join, Fn::Sub, Fn::If and Ref are
        resolved so literal text carried inside them counts toward the 4 KB
        aggregate. Scenarios that cannot be resolved to a string contribute
        nothing, preserving the previous behavior for unknown values.
        """
        max_size = 0
        for resolved_value, _, resolved_errs in validator.resolve_value(value):
            if resolved_errs:
                continue
            if isinstance(resolved_value, str):
                max_size = max(max_size, len(resolved_value.encode("utf-8")))
        return max_size
