"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_appstream_fleet
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class FleetInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3621"
    shortdesc = "Validate the instance types for AppStream Fleet"
    description = (
        "Validates the AppStream Fleet instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::AppStream::Fleet/Properties/InstanceType"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_appstream_fleet,
                filename="instancetype_enum.json",
            ),
        )
