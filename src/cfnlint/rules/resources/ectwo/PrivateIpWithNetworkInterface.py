"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_instance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class PrivateIpWithNetworkInterface(CfnLintJsonSchema):
    id = "E3674"
    shortdesc = "Primary cannoy be True when PrivateIpAddress is specified"
    description = "Only specify the private IP address for an instance in one spot"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::Instance/Properties",
                "Resources/AWS::EC2::NetworkInterface/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_instance,
                filename="privateipaddress.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "'Primary' cannot be True when 'PrivateIpAddress' is specified"
