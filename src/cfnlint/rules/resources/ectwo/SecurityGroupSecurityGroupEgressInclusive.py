"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupSecurityGroupEgressInclusive(BaseCfnSchema):
    id = "E3665"
    shortdesc = "Validate SG egress you must have VpcId"
    description = "When you specify 'SecurityGroupEgress' you must specify 'VpcId'"
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroup/securitygroupegress_inclusive"
