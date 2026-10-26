"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_autoscaling_launchconfiguration
import cfnlint.data.schemas.extensions.aws_ec2_instance
import cfnlint.data.schemas.extensions.aws_ec2_securitygroup
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema

_launch_configuration = (
    "Resources/AWS::AutoScaling::LaunchConfiguration"
    "/Properties/BlockDeviceMappings/*/Ebs"
)


class Ebs(CfnLintJsonSchema):
    id = "E3671"
    shortdesc = "Validate block device mapping configuration"
    description = "Certain volume types require Iops to be specified"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                _launch_configuration,
                "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
            ],
        )
        self._schema = load_resource(
            cfnlint.data.schemas.extensions.aws_ec2_instance,
            filename="blockdevicemappings.json",
        )
        # Auto Scaling allows a lower gp3 Iops maximum than EC2 does
        self._launch_configuration_schema = load_resource(
            cfnlint.data.schemas.extensions.aws_autoscaling_launchconfiguration,
            filename="blockdevicemappings.json",
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        if err.validator in ("minimum", "maximum"):
            return err.message

        return (
            "'Iops' is a required property when 'VolumeType' has a value "
            f"of {instance.get('VolumeType')!r}"
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if keywords == _launch_configuration:
            schema = self._launch_configuration_schema
        else:
            schema = self._schema

        yield from super().validate(validator, keywords, instance, schema)
