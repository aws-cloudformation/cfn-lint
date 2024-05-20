"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.other.metadata
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class InterfaceConfiguration(CfnLintJsonSchema):
    """Check if Metadata Interface Configuration are configured correctly"""

    id = "E4001"
    shortdesc = "Metadata Interface have appropriate properties"
    description = "Metadata Interface properties are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html"
    tags = ["metadata"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Metadata/AWS::CloudFormation::Interface"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.metadata, "interface.json"
            ),
            all_matches=True,
        )
