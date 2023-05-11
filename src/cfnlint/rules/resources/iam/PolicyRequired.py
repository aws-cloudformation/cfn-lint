"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class PolicyRequired(BaseCfnSchema):
    id = "E3636"
    shortdesc = "Validate IAM Policy has one of the required properties"
    description = "Specify at least one of 'Groups', 'Roles' and 'Users'"
    tags = ["resources"]
    schema_path = "aws_iam_policy/required"
