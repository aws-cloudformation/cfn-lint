"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class BucketWebsiteConfigurationRedirectAllRequestsToExclusive(BaseCfnSchema):
    id = "E3656"
    shortdesc = (
        "Validate S3 bucket redirect all requests properties aren't used together"
    )
    description = (
        "Specify at least one of 'HttpErrorCodeReturnedEquals' and 'KeyPrefixEquals'"
    )
    tags = ["resources"]
    schema_path = "aws_s3_bucket/routingrulecondition_required"
