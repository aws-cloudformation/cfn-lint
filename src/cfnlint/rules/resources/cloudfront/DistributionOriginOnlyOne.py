"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DistributionOriginOnlyOne(BaseCfnSchema):
    id = "E3645"
    shortdesc = "Validate CloudFront has either custom or s3 origins"
    description = "Specify only 'CustomOriginConfig' or 'S3OriginConfig'"
    tags = ["resources"]
    schema_path = "aws_cloudfront_distribution/origin_onlyone"
