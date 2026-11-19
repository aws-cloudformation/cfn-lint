"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
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
                "Resources/AWS::EC2::Volume/Properties",
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

        # A standalone gp3 volume has a baseline of 3,000 IOPS and permits
        # additional provisioned IOPS at most 500 per GiB of volume size.
        # Block device mappings use VolumeSize, while standalone
        # AWS::EC2::Volume properties use Size. The Size guard below
        # therefore scopes this check to standalone volumes without
        # relying on a path string passed through the rule runner.
        if not isinstance(instance, dict) or instance.get("VolumeType") != "gp3":
            return

        size = instance.get("Size")
        iops = instance.get("Iops")

        # Intrinsic functions cannot be compared until their values resolve.
        if type(size) is not int or type(iops) is not int or size <= 0:
            return

        max_iops = max(3000, 500 * size)

        # IOPS greater than 80,000 are already reported by the schema.
        if max_iops < iops <= 80000:
            yield ValidationError(
                f"{iops} IOPS exceeds the gp3 size-based limit "
                f"of {max_iops} IOPS for a {size} GiB volume",
                rule=self,
                path=deque(["Iops"]),
            )
