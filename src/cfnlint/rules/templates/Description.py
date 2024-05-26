"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.other.template
from cfnlint.rules import CfnLintJsonSchema, SchemaDetails


class Description(CfnLintJsonSchema):
    """Check Template Description is only a String"""

    id = "E1004"
    shortdesc = "Template description can only be a string"
    description = "Template description can only be a string"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-description-structure.html"
    tags = ["description"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Description"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.template,
                "description.json",
            ),
            all_matches=True,
        )
        self.rule_set = {
            "maxLength": "E1003",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
