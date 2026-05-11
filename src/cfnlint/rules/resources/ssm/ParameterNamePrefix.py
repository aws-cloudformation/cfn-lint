"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class ParameterNamePrefix(CfnLintKeyword):
    id = "W3701"
    shortdesc = "SSM Parameter Name should not use /aws/ or /ssm/ prefix"
    description = (
        "SSM parameter names starting with /aws/ or /ssm/ (or aws/ssm "
        "without a leading slash) are reserved. While some AWS services "
        "can create parameters in this namespace, most users cannot."
    )
    source_url = "https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-su-create.html"
    tags = ["resources", "ssm"]

    def __init__(self) -> None:
        super().__init__(["Resources/AWS::SSM::Parameter/Properties/Name"])
        self._pattern = re.compile(
            r"^(?i)((?!aws|ssm)[\w.-]+|\/(?!aws|ssm)[\w.-]+(\/[\w.-]+)*)$"
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, str):
            return

        if not self._pattern.match(instance):
            yield ValidationError(
                f"{instance!r} does not match the recommended pattern. "
                "Parameter names beginning with 'aws' or 'ssm' are "
                "reserved and may not be available for all users."
            )
