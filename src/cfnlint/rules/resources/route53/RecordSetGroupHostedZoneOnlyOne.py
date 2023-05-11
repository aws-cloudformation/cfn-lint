"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class RecordSetGroupHostedZoneOnlyOne(BaseCfnSchema):
    id = "E3674"
    shortdesc = "Validate Route53 record set has either Hosted Zone Id or Name"
    description = "Specify only 'HostedZoneId' or 'HostedZoneName'"
    tags = ["resources"]
    schema_path = "aws_route53_recordsetgroup/hostedzone_onlyone"
