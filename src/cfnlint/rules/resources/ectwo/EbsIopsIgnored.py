"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

_no_iops_volume_types = {"gp2", "st1", "sc1", "standard"}


class EbsIopsIgnored(CfnLintKeyword):
    id = "W3671"
    shortdesc = "Iops is ignored for certain EBS volume types"
    description = (
        "When Iops is specified with volume types gp2, st1, sc1, or standard, "
        "the value is silently ignored. Remove Iops or use a volume type "
        "that supports provisioned IOPS (io1, io2, gp3)."
    )
    source_url = (
        "https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html"
    )
    tags = ["resources", "ec2", "ebs"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::OpsWorks::Instance/Properties/BlockDeviceMappings/*/Ebs",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        volume_type = instance.get("VolumeType")
        if not isinstance(volume_type, str):
            return

        if volume_type.lower() in _no_iops_volume_types and "Iops" in instance:
            yield ValidationError(
                f"'Iops' is ignored when 'VolumeType' is {volume_type!r}",
                path=["Iops"],
            )
