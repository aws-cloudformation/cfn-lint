"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DistributionViewerCertificateOnlyOne(BaseCfnSchema):
    id = "E3642"
    shortdesc = "Validate CloudFront viewer cert doesn't include exlusive properties"
    description = "Specify only 'AcmCertificateArn', 'CloudFrontDefaultCertificate', or 'IamCertificateId'"
    tags = ["resources"]
    schema_path = "aws_cloudfront_distribution/viewercertificate_onlyone"
