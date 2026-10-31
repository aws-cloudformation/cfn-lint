"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

_VOLUME_PATH = "Resources/AWS::EC2::Volume/Properties"
_IOPS_PER_GIB = {"gp3": 500, "io1": 50, "io2": 1000}


class EbsIopsRatio(CfnLintKeyword):
    id = "E3662"
    shortdesc = "Validate EBS IOPS-to-volume-size ratios"
    description = (
        "EBS gp3, io1, and io2 volumes limit provisioned IOPS relative "
        "to volume size. The gp3 baseline of 3000 IOPS is always allowed."
    )
    source_url = (
        "https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html"
    )
    tags = ["resources", "ec2", "ebs"]

    def __init__(self, keywords: list[str] | None = None) -> None:
        super().__init__(
            keywords
            if keywords is not None
            else [
                _VOLUME_PATH,
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*/Ebs",
            ]
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        volume_type = instance.get("VolumeType")
        if not isinstance(volume_type, str):
            return

        ratio = _IOPS_PER_GIB.get(volume_type)
        if ratio is None:
            return

        size_key = "Size" if keywords == _VOLUME_PATH else "VolumeSize"
        size = instance.get(size_key)
        iops = instance.get("Iops")

        # Leave unresolved intrinsics and invalid types to the other rules.
        # A missing block device VolumeSize can also inherit an AMI's size.
        if type(size) is not int or type(iops) is not int or size <= 0:
            return

        limit = size * ratio
        if volume_type == "gp3":
            limit = max(3000, limit)

        if iops > limit:
            yield ValidationError(
                f"{iops} IOPS exceeds the {volume_type} maximum of {limit} "
                f"for a {size} GiB volume (ratio {ratio}:1)",
                path=["Iops"],
            )


class EbsIopsRatioWarning(EbsIopsRatio):
    id = "W3662"
    shortdesc = "Warn about EBS IOPS ratios checked only at instance launch"
    description = (
        "Launch templates and Spot Fleets are not checked for EBS IOPS-to-size "
        "ratios when a stack is created, but invalid values fail at launch."
    )

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*/Ebs",
            ]
        )
