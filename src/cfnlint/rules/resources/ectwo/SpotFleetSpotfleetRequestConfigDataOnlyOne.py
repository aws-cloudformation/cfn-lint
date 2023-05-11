"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SpotFleetSpotfleetRequestConfigDataOnlyOne(BaseCfnSchema):
    id = "E3654"
    shortdesc = "Validate SpotFleet has only launch specifications or template configs"
    description = "Specify only 'LaunchSpecifications' or 'LaunchTemplateConfigs'"
    tags = ["resources"]
    schema_path = "aws_ec2_spotfleet/spotfleetrequestconfigdata_onlyone"
