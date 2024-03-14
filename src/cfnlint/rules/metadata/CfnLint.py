"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.data.schemas.other import metadata as schema_metadata
from cfnlint.helpers import load_resource
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class CfnLint(BaseJsonSchema):
    """Check if Metadata Interface Configuration are configured correctly"""

    id = "W4005"
    shortdesc = "Validate cfnlint configuration in the Metadata"
    description = (
        "Metadata cfn-lint configuration has many values and we want to validate that"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html"
    tags = ["metadata"]

    def __init__(self) -> None:
        super().__init__()
        self.rule_set = {}
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self._schema = load_resource(schema_metadata, "cfn_lint.json")
        self.cfnmetadatacfnlint = self.validate

    @property
    def schema(self):
        return self._schema
