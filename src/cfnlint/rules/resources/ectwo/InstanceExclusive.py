"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class InstanceExclusive(BaseCfnSchema):
    id = "E3629"
    shortdesc = "Validate EC2 instance have NetworkInterfaces or SubnetId"
    description = "Specify only 'NetworkInterfaces' or 'SubnetId'"
    tags = ["resources"]
    schema_path = "aws_ec2_instance/exclusive"
