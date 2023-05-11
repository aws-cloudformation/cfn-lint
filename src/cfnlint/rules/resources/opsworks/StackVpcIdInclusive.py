"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class StackVpcIdInclusive(BaseCfnSchema):
    id = "E3671"
    shortdesc = "Validate OpsWork stack has either vpc or default subnet"
    description = "When you specify 'VpcId' you must specify 'DefaultSubnetId'"
    tags = ["resources"]
    schema_path = "aws_opsworks_stack/vpcid_inclusive"
