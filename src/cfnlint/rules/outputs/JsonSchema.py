"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import outputs as schema_outputs
from cfnlint.helpers import REGION_PRIMARY, load_resource
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class JsonSchema(BaseJsonSchema):
    """Check Base Outputs Configuration"""

    id = "E6000"
    shortdesc = "JSON Schema validation of the CloudFormation outputs"
    description = "Making sure that outputs comply with the JSON schema"
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
            "awsType": "E6100",
            "ref": "E1020",
            "fn_base64": "E1021",
            "fn_cidr": "E1024",
            "fn_findinmap": "E1011",
            "fn_foreach": "E1032",
            "fn_getatt": "E1010",
            "fn_getazs": "E1015",
            "fn_if": "E1028",
            "fn_importvalue": "E1016",
            "fn_join": "E1022",
            "fn_length": "E1030",
            "fn_select": "E1017",
            "fn_split": "E1018",
            "fn_sub": "E1019",
            "fn_tojsonstring": "E1031",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.regions = [REGION_PRIMARY]
        self.schema = load_resource(schema_outputs, "configuration.json")

    def initialize(self, cfn):
        self.regions = cfn.regions
        return super().initialize(cfn)

    def match(self, cfn):
        """Check CloudFormation Outputs"""
        matches = []

        outputs = cfn.template.get("Outputs", {})

        cfn_validator = self.setup_validator(
            validator=CfnTemplateValidator,
            schema=self.schema,
            context=cfn.context.create_context_for_outputs(cfn.regions),
        ).evolve(
            cfn=cfn,
        )

        matches.extend(self.json_schema_validate(cfn_validator, outputs, ["Outputs"]))

        return matches
