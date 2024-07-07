"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.other.transforms
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    """Check if Parameters are configured correctly"""

    id = "E1005"
    shortdesc = "Validate Transform configuration"
    description = (
        "Validate that the transforms section of a template is properly configured"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/transform-section-structure.html"
    tags = ["transform"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Transform"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.transforms, "configuration.json"
            ),
            all_matches=True,
        )
