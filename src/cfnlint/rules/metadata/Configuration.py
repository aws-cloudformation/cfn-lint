"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.other.metadata
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    """Check if Metadata configuration is properly configured"""

    id = "E4002"
    shortdesc = "Validate the configuration of the Metadata section"
    description = "Validates that Metadata section is an object and has no null values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/metadata-section-structure.html"
    tags = ["metadata"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Metadata"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.metadata, "configuration.json"
            ),
            all_matches=True,
        )
