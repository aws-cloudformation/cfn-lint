"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.data.schemas.other import mappings as schema_mappings
from cfnlint.helpers import load_resource
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):
    """Check if Mappings are configured correctly"""

    id = "E7001"
    shortdesc = "Mappings are appropriately configured"
    description = "Check if Mappings are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html"
    tags = ["mappings"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "additionalProperties": "E7001",
            "patternProperties": "E7001",
            "properties": "E7001",
            "propertyNames": "E7002",
            "maxProperties": "E7010",
            "minProperties": "E7001",
            "required": "E7001",
            "type": "E7001",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.cfnmappings = self.validate
        self._schema = load_resource(schema_mappings, "configuration.json")

    @property
    def schema(self):
        return self._schema
