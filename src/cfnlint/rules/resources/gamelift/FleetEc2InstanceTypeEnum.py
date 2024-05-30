"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_gamelift_fleet
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class FleetEc2InstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3641"
    shortdesc = "Validate GameLift Fleet EC2 instance type"
    description = (
        "Validates the GameLift Fleet EC2 instance types based on "
        "region and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::GameLift::Fleet/Properties/EC2InstanceType"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_gamelift_fleet,
                filename="ec2instancetype_enum.json",
            ),
        )
