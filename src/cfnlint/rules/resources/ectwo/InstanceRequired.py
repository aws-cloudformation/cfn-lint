"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class InstanceRequired(BaseCfnSchema):
    id = "E3632"
    shortdesc = "Validate EC2 Instance has required properties"
    description = "Specify at least one of 'ImageId' and 'LaunchTemplate'"
    tags = ["resources"]
    schema_path = "aws_ec2_instance/required"
