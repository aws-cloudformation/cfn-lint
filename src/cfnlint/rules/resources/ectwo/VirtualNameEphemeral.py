"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

# EC2 uses the first of these a block device mapping specifies, highest first
_PRECEDENCE = ["Ebs", "VirtualName", "NoDevice"]


class VirtualNameIgnored(CfnLintKeyword):
    id = "W3698"
    shortdesc = "Lower precedence block device mapping properties are ignored"
    description = (
        "EC2 uses the first of 'Ebs', 'VirtualName' and 'NoDevice' that a block "
        "device mapping specifies and silently ignores the others. Remove the "
        "properties that have no effect."
    )
    source_url = "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        # only the types whose schema allows the combination; elsewhere
        # requiredXor already reports it as an error (E3014)
        super().__init__(
            [
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*",
                (
                    "Resources/AWS::EC2::LaunchTemplate/Properties/"
                    "LaunchTemplateData/BlockDeviceMappings/*"
                ),
            ]
        )

    def _is_required_xor(self, validator: Validator) -> bool:
        schema = validator.schema
        if not isinstance(schema, dict):
            return False
        required_xor = schema.get("requiredXor") or []
        return len([k for k in _PRECEDENCE if k in required_xor]) > 1

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        # don't warn about what E3014 already reports as an error
        if self._is_required_xor(validator):
            return

        ignored: dict[str, str] = {}
        for scenario, _status in validator.context.conditions.evolve_from_instance(
            instance, context=validator.context
        ):
            if not isinstance(scenario, dict):
                continue
            keys = [k for k in _PRECEDENCE if k in scenario]
            for key in keys[1:]:
                ignored.setdefault(key, keys[0])

        for key in _PRECEDENCE:
            if key in ignored:
                yield ValidationError(
                    f"{key!r} is ignored when {ignored[key]!r} is specified",
                    path=[key],
                )
