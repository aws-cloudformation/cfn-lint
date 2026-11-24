"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_instance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class EbsWarning(CfnLintJsonSchema):
    id = "W3672"
    shortdesc = "Validate block device mappings that are only checked at launch"
    description = (
        "Launch templates and Spot Fleet launch specifications are not "
        "validated when the stack is created, so a missing or out of range "
        "Iops for certain volume types only fails when instances are launched"
    )
    source_url = (
        "https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html"
    )
    tags = ["resources", "ec2", "ebs"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*/Ebs",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_instance,
                filename="blockdevicemappings.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        if err.validator in ("minimum", "maximum"):
            return err.message

        return (
            "'Iops' is a required property when 'VolumeType' has a value "
            f"of {instance.get('VolumeType')!r}"
        )
