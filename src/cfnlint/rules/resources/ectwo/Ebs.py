"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_instance
import cfnlint.data.schemas.extensions.aws_ec2_securitygroup
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Ebs(CfnLintJsonSchema):
    id = "E3671"
    shortdesc = "Validate block device mapping configuration"
    description = "Certain volume types require Iops to be specified"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*/Ebs",
                "Resources/AWS::OpsWorks::Instance/Properties/BlockDeviceMappings/*/Ebs",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_instance,
                filename="blockdevicemappings.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        if err.schema_path[0] == "allOf":
            if err.schema_path[1] == 1:
                return (
                    "Additional properties are not allowed (Iops) "
                    "was unexpected when 'VolumeType' has a value "
                    f"of {instance.get('VolumeType')!r}"
                )

        return (
            f"'Iops' is a required property when 'VolumeType' has a value "
            f"of {instance.get('VolumeType')!r}"
        )
