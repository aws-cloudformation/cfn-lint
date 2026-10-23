"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
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
        "This rule measures the size of the compact JSON encoding of the "
        "variables and validates the total does not exceed 4096 bytes."
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

        variables: dict[str, str] = {}
        for key, value in instance.items():
            if not isinstance(key, str):
                continue
            if isinstance(value, str):
                variables[key] = value

        # Lambda measures the variables as compact JSON, so the structural
        # characters (quotes, colons, commas and braces) count toward the
        # limit. Measure the UTF-8 byte length of the compact encoding
        # instead of summing key and value lengths.
        total_size = len(
            json.dumps(variables, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        )

        max_size = 4096
        if total_size > max_size:
            yield ValidationError(
                f"Lambda environment variables total size ({total_size}) "
                f"exceeds the 4 KB ({max_size} bytes) limit",
                rule=self,
            )
