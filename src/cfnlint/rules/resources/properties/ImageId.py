"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules import CloudFormationLintRule


class ImageId(CloudFormationLintRule):
    id = "W2506"
    shortdesc = "Check if ImageId Parameters have the correct type"
    description = (
        "See if there are any refs for ImageId to a parameter "
        + "of inappropriate type. Appropriate Types are "
        + "[AWS::EC2::Image::Id, AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>]"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes"
    tags = ["parameters", "ec2", "imageid"]

    def validate(self, validator: Validator, _, instance: Any, schema: Any):
        value = instance.get("Ref")
        if value not in validator.context.parameters:
            return

        parameter_type = validator.context.parameters[value].type
        for err in validator.descend(
            parameter_type,
            {
                "enum": [
                    "AWS::EC2::Image::Id",
                    "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
                ]
            },
        ):
            err.rule = self
            err.path_override = deque(["Parameters", value, "Type"])
            yield err
