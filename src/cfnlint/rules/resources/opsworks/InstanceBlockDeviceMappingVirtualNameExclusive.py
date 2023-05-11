"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class InstanceBlockDeviceMappingVirtualNameExclusive(BaseCfnSchema):
    id = "E3659"
    shortdesc = "Validate OpsWorks block device mapping VirtualName with Ebs"
    description = "When you specify 'VirtualName' do not specify 'Ebs'"
    tags = ["resources"]
    schema_path = "aws_opsworks_instance/blockdevicemapping_virtualname_exclusive"
