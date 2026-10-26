"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

_gp3_baseline_iops = 3000
_gp3_minimum_iops = 100


class EbsIopsAdjusted(CfnLintKeyword):
    id = "W3673"
    shortdesc = "Iops below the gp3 baseline is raised rather than rejected"
    description = (
        "EC2 does not reject a gp3 'Iops' between 100 and 2999. It raises the "
        "volume to the gp3 baseline of 3000, so the stack deploys and the "
        "provisioned IOPS is not the value written in the template"
    )
    source_url = "https://docs.aws.amazon.com/ebs/latest/userguide/general-purpose.html"
    tags = ["resources", "ec2", "ebs"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        volume_type = instance.get("VolumeType")
        if not isinstance(volume_type, str) or volume_type.lower() != "gp3":
            return

        iops = instance.get("Iops")
        # a bool is an int in Python, and a non scalar is an unresolved
        # function that this rule cannot speak to
        if isinstance(iops, bool) or not isinstance(iops, (int, str)):
            return

        try:
            iops = int(iops)
        except ValueError:
            return

        # below the minimum the volume is rejected outright, and E3671
        # already reports that
        if _gp3_minimum_iops <= iops < _gp3_baseline_iops:
            yield ValidationError(
                f"'Iops' of {iops} is raised to {_gp3_baseline_iops} for "
                f"'VolumeType' {volume_type!r}",
                path=["Iops"],
            )
