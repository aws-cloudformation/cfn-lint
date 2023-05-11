"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DistributionViewerCertificateIamCertificateIdInclusive(BaseCfnSchema):
    id = "E3646"
    shortdesc = "Validate CloudFront viewer certificate with ID also has ssl support method"
    description = (
        "When you specify 'IamCertificateId' you must specify 'SslSupportMethod'"
    )
    tags = ["resources"]
    schema_path = (
        "aws_cloudfront_distribution/viewercertificate_iamcertificateid_inclusive"
    )
