"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupAllToAndFromPorts(BaseCfnSchema):
    id = "E3688"
    shortdesc = "Validate that to and from ports are both -1"
    description = "When ToPort or FromPort are -1 the other one must also be -1"
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroup/all_to_and_from_ports"

    def message(self, instance: Any, err: ValidationError) -> str:
        if not isinstance(instance, dict):
            return self.description

        return "Both ['FromPort', 'ToPort'] must be -1 when one is -1"
