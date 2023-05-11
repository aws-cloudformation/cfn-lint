"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class RecordSetHostedZoneOnlyOne(BaseCfnSchema):
    id = "E3625"
    shortdesc = "Validate record set doesn't have ID or Name"
    description = "Specify only 'HostedZoneId' or 'HostedZoneName'"
    tags = ["resources"]
    schema_path = "aws_route53_recordset/hostedzone_onlyone"
