"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupIngressSourceSecurityGroupIdExclusive(BaseCfnSchema):
    id = "E3664"
    shortdesc = "Validate SG ingress doesn't use ID with Name"
    description = "When you specify 'GroupId' do not specify 'GroupName'"
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroup/ingress_sourcesecuritygroupid_exclusive"
