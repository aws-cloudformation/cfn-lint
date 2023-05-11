"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class NetworkAclEntryRequired(BaseCfnSchema):
    id = "E3680"
    shortdesc = "Validate EC2 network ACL has either Ipv4 or Ipv6"
    description = "Specify at least one of 'Ipv6CidrBlock' and 'CidrBlock'"
    tags = ["resources"]
    schema_path = "aws_ec2_networkaclentry/required"
