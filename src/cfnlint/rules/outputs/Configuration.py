"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import outputs as schema_outputs
from cfnlint.helpers import load_resource
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):
    """Check Base Outputs Configuration"""

    id = "E6001"
    shortdesc = "Check the properties of Outputs"
    description = "Validate the property structure for outputs"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "additionalProperties": "E6001",
            "patternProperties": "E6001",
            "properties": "E6001",
            "propertyNames": "E6004",
            "required": "E6002",
            "type": "E6003",
            "maxProperties": "E6010",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self._schema = load_resource(schema_outputs, "configuration.json")
        self.cfnoutputs = self.validate

    @property
    def schema(self):
        return self._schema
