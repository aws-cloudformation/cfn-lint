"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_instance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class EbsIopsAdjusted(CfnLintJsonSchema):
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
            keywords=[
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_instance,
                filename="blockdevicemappings_gp3_iops.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            f"'Iops' of {instance.get('Iops')} is raised to 3000 for "
            f"'VolumeType' {instance.get('VolumeType')!r}"
        )
