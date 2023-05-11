"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class BucketWebsiteConfigurationRedirectAllRequestsToExclusive(BaseCfnSchema):
    id = "E3657"
    shortdesc = (
        "Validate S3 bucket website configuration properties can't be used " "together"
    )
    description = (
        "When you specify 'RedirectAllRequestsTo' do not specify "
        "'ErrorDocument', 'IndexDocument', or 'RoutingRules'"
    )
    tags = ["resources"]
    schema_path = "aws_s3_bucket/websiteconfiguration_redirectallrequeststo_exclusive"
