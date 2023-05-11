"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class TableBillingModeExclusive(BaseCfnSchema):
    id = "E3638"
    shortdesc = (
        "Validate DynamoDB BillingMode pay per request configuration"
    )
    description = (
        "When 'BillingMode' is 'PAY_PER_REQUEST' don't specify 'ProvisionedThroughput'"
    )
    tags = ["resources"]
    schema_path = "aws_dynamodb_table/billingmode_exclusive"
