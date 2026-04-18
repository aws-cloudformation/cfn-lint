"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class VirtualNameIgnored(CfnLintKeyword):
    id = "W3698"
    shortdesc = "VirtualName is ignored when Ebs is specified"
    description = (
        "When both VirtualName and Ebs are specified in a block device mapping, "
        "VirtualName is silently ignored by EC2. Remove VirtualName or Ebs."
    )
    source_url = "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*",
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*",
                "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*",
                "Resources/AWS::OpsWorks::Instance/Properties/BlockDeviceMappings/*",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        if "VirtualName" in instance and "Ebs" in instance:
            yield ValidationError(
                "'VirtualName' is ignored when 'Ebs' is specified",
                path=["VirtualName"],
            )
