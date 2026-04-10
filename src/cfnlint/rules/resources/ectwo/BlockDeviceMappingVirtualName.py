"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_instance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class BlockDeviceMappingVirtualName(CfnLintJsonSchema):
    id = "E3715"
    shortdesc = "VirtualName must use ephemeral device format when Ebs is absent"
    description = (
        "When specifying VirtualName without Ebs in a block device mapping, "
        "the value must match 'ephemeralN' (N=0-23) or the deployment will fail."
    )
    source_url = "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*",
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*",
                "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*",
                "Resources/AWS::OpsWorks::Instance/Properties/BlockDeviceMappings/*",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_instance,
                filename="virtualname_ephemeral.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            f"{instance.get('VirtualName')!r} is not a valid ephemeral device name. "
            "Expected format is 'ephemeralN' where N is 0-23"
        )
