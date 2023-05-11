"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupIngressCidrIpExclusive(BaseCfnSchema):
    id = "E3666"
    shortdesc = "Validate ingress rules don't use CidrIp with other properties"
    description = "When you specify 'CidrIp' do not specify 'SourceSecurityGroupName', 'SourceSecurityGroupId', or 'CidrIpv6'"
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroup/ingress_cidrip_exclusive"
