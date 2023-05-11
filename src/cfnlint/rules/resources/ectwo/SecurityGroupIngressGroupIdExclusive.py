"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupIngressGroupIdExclusive(BaseCfnSchema):
    id = "E3673"
    shortdesc = "Validate SG ingress either uses Id or Name"
    description = "When you specify 'SourceSecurityGroupId' do not specify 'SourceSecurityGroupName'"
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroupingress/groupid_exclusive"
