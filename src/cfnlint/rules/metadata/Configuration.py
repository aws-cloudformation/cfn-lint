"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.data.schemas.other import metadata as schema_metadata
from cfnlint.helpers import load_resource
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):
    """Check if Metadata configuration is properly configured"""

    id = "E4002"
    shortdesc = "Validate the configuration of the Metadata section"
    description = "Validates that Metadata section is an object and has no null values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/metadata-section-structure.html"
    tags = ["metadata"]

    def __init__(self) -> None:
        super().__init__()
        self.rule_set = {}
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self._schema = load_resource(schema_metadata, "configuration.json")
        self.cfnmetadata = self.validate

    @property
    def schema(self):
        return self._schema
