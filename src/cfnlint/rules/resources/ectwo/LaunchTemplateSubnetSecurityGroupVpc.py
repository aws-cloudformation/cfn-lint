"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_launchtemplate
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class LaunchTemplateSubnetSecurityGroupVpc(CfnLintJsonSchema):
    id = "E3714"
    shortdesc = "Validate LaunchTemplate SecurityGroup and Subnet are in the same VPC"
    description = (
        "When a LaunchTemplate references SecurityGroups via "
        "'SecurityGroupIds' and Subnets via 'NetworkInterfaces', "
        "the SecurityGroup's VpcId must match the Subnet's VpcId"
    )
    source_url = (
        "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html"
    )
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::LaunchTemplate/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_launchtemplate,
                filename="launch_template_sg_subnet_vpc.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "SecurityGroup VpcId does not match Subnet VpcId in the LaunchTemplate"

    def _clean_error(self, err: ValidationError) -> ValidationError:
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
