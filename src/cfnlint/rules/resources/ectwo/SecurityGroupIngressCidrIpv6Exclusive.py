"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupIngressCidrIpv6Exclusive(BaseCfnSchema):
    id = "E3663"
    shortdesc = "Validate SG Ingress doesn't have properties when using Ipv6"
    description = "When you specify 'CidrIpv6' do not specify 'SourceSecurityGroupName' or 'SourceSecurityGroupId'"
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroup/ingress_cidripv6_exclusive"
