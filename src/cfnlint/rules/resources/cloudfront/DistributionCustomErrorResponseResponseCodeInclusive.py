"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DistributionCustomErrorResponseResponseCodeInclusive(BaseCfnSchema):
    id = "E3644"
    shortdesc = "Validate CloudFront response code includes page path"
    description = "When you specify 'ResponseCode' you must specify 'ResponsePagePath'"
    tags = ["resources"]
    schema_path = (
        "aws_cloudfront_distribution/customerrorresponse_responsecode_inclusive"
    )
