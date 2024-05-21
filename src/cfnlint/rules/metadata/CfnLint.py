"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.other.metadata
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class CfnLint(CfnLintJsonSchema):
    """Check if Metadata Interface Configuration are configured correctly"""

    id = "W4005"
    shortdesc = "Validate cfnlint configuration in the Metadata"
    description = (
        "Metadata cfn-lint configuration has many values and we want to validate that"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html"
    tags = ["metadata"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Metadata/cfn-lint"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.metadata, "cfn_lint.json"
            ),
            all_matches=True,
        )
