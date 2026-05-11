"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_ec2_vpngateway
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class VpnGatewayType(CfnLintJsonSchema):
    id = "W3703"
    shortdesc = "VPNGateway Type should be ipsec.1"
    description = (
        "The only supported value for AWS::EC2::VPNGateway "
        "Type is 'ipsec.1'. Other values may not be available."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpngateway.html"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::VPNGateway/Properties/Type",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_vpngateway,
                filename="type_enum.json",
            ),
            all_matches=True,
        )
