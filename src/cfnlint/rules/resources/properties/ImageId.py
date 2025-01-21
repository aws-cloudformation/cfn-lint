"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class ImageId(CfnLintKeyword):
    id = "W2506"
    shortdesc = "Check if ImageId Parameters have the correct type"
    description = (
        "See if there are any refs for ImageId to a parameter "
        + "of inappropriate type. Appropriate Types are "
        + "[AWS::EC2::Image::Id, AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>]"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes"
    tags = ["parameters", "ec2", "imageid"]

    def __init__(self):
        super().__init__(
            keywords=[
                "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/ImageId",
                "Resources/AWS::Batch::ComputeEnvironment/Properties/ComputeResources/ImageId",
                "Resources/AWS::Cloud9::EnvironmentEC2/Properties/ImageId",
                "Resources/AWS::EC2::Instance/Properties/ImageId",
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/ImageId",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/ImageId",
                "Resources/AWS::ImageBuilder::Image/Properties/ImageId",
            ]
        )
        self.parent_rules = ["E1020"]

    def validate(self, validator: Validator, _, instance: Any, schema: Any):
        if any(fn in validator.context.path.path for fn in FUNCTIONS):
            return

        if instance not in validator.context.parameters:
            return

        parameter_type = validator.context.parameters[instance].type
        for err in validator.descend(
            instance=parameter_type,
            schema={
                "enum": [
                    "AWS::EC2::Image::Id",
                    "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
                ]
            },
        ):
            err.rule = self
            err.path_override = deque(["Parameters", instance, "Type"])
            yield err
