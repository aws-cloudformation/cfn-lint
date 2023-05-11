"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DistributionViewerCertificateAcmCertificateArnInclusive(BaseCfnSchema):
    id = "E3643"
    shortdesc = (
        "Validate CloudFront viewer certificate arn includes ssl support method"
    )
    description = (
        "When you specify 'AcmCertificateArn' you must specify 'SslSupportMethod'"
    )
    tags = ["resources"]
    schema_path = (
        "aws_cloudfront_distribution/viewercertificate_acmcertificatearn_inclusive"
    )
