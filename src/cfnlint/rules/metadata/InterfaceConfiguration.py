"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.data.schemas.other import metadata as schema_metadata
from cfnlint.helpers import load_resource
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class InterfaceConfiguration(BaseJsonSchema):
    """Check if Metadata Interface Configuration are configured correctly"""

    id = "E4001"
    shortdesc = "Metadata Interface have appropriate properties"
    description = "Metadata Interface properties are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html"
    tags = ["metadata"]

    def __init__(self) -> None:
        super().__init__()
        self.rule_set = {}
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self._schema = load_resource(schema_metadata, "interface.json")
        self.cfnmetadatainterface = self.validate

    @property
    def schema(self):
        return self._schema
