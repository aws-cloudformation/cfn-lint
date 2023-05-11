"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class LoadBalancerSubnetsOnlyOne(BaseCfnSchema):
    id = "E3669"
    shortdesc = "Validate ELBv2 has either subnet mappings or subnets"
    description = "Specify only 'SubnetMappings' or 'Subnets'"
    tags = ["resources"]
    schema_path = "aws_elasticloadbalancingv2_loadbalancer/subnets_onlyone"
