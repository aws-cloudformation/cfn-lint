"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import parameters as schema_parameters
from cfnlint.helpers import REGION_PRIMARY, load_resource
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules.jsonschema.base import BaseJsonSchema


class JsonSchema(BaseJsonSchema):
    """Check Base Parameter Configuration"""

    id = "E2000"
    shortdesc = "JSON Schema validation of the CloudFormation parameters"
    description = "Making sure that parameters comply with the JSON schema"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html"
    tags = ["parameters"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "additionalProperties": "E2001",
            "patternProperties": "E2001",
            "properties": "E2001",
            "propertyNames": "E2003",
            "maxProperties": "E2010",
            "minProperties": "E2010",
            "required": "E2001",
            "type": "E2001",
            "enum": "E2002",
            "maxLength": "E2012",
            "maximum": "E2012",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.regions = [REGION_PRIMARY]
        self.schema = load_resource(schema_parameters, "configuration.json")
        self.validators["type"] = cfn_type

    def match(self, cfn):
        """Check CloudFormation Parameters"""
        matches = []

        mappings = cfn.template.get("Parameters", {})

        cfn_validator = self.setup_validator(
            validator=CfnTemplateValidator,
            schema=self.schema,
            context=cfn.context.create_context_for_parameters(cfn.regions),
        ).evolve(
            cfn=cfn,
        )

        matches.extend(
            self.json_schema_validate(cfn_validator, mappings, ["Parameters"])
        )

        return matches
