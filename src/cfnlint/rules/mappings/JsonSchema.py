"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import mappings as schema_mappings
from cfnlint.helpers import REGION_PRIMARY, load_resource
from cfnlint.jsonschema import StandardValidator
from cfnlint.rules.jsonschema.base import BaseJsonSchema


class JsonSchema(BaseJsonSchema):
    """Check Base Outputs Configuration"""

    id = "E7000"
    shortdesc = "JSON Schema validation of the CloudFormation mappings"
    description = "Making sure that mappings comply with the JSON schema"
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
        self.regions = [REGION_PRIMARY]
        self.schema = load_resource(schema_mappings, "configuration.json")

    def match(self, cfn):
        """Check CloudFormation Outputs"""
        matches = []

        mappings = cfn.template.get("Mappings", {})

        cfn_validator = self.setup_validator(
            validator=StandardValidator,
            schema=self.schema,
            context=cfn.context.create_context_for_mappings(cfn.regions),
        ).evolve(
            cfn=cfn,
        )

        matches.extend(self.json_schema_validate(cfn_validator, mappings, ["Mappings"]))

        return matches
