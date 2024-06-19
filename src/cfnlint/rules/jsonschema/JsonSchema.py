"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint._typing import RuleMatches
from cfnlint.data.schemas.other import template as schema_template
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.jsonschema._keywords_cfn import cfn_type
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.template import Template


class JsonSchema(BaseJsonSchema):
    """Check Base Template Settings"""

    id = "E1001"
    shortdesc = "Basic CloudFormation Template Configuration"
    description = (
        "Making sure the basic CloudFormation template components are properly"
        " configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["base"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "cfnLint": "E1101",
            "condition": "E8007",
            "dynamicReference": "E1050",
            "fn_and": "E8004",
            "fn_base64": "E1021",
            "fn_cidr": "E1024",
            "fn_equals": "E8003",
            "fn_findinmap": "E1011",
            "fn_foreach": "E1032",
            "fn_getatt": "E1010",
            "fn_getazs": "E1015",
            "fn_if": "E1028",
            "fn_importvalue": "E1016",
            "fn_join": "E1022",
            "fn_length": "E1030",
            "fn_not": "E8005",
            "fn_or": "E8006",
            "fn_select": "E1017",
            "fn_split": "E1018",
            "fn_sub": "E1019",
            "fn_tojsonstring": "E1031",
            "format": "E1103",
            "ref": "E1020",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.config_definition = {"sections": {"default": "", "type": "string"}}
        self.configure()
        self.validators = {
            "type": cfn_type,
        }

    @property
    def schema(self):
        schema = load_resource(schema_template, "configuration.json")
        if self.config["sections"]:
            schema["properties"][self.config["sections"]] = True

        return schema

    def match(self, cfn: Template) -> RuleMatches:
        """Check CloudFormation Parameters"""
        matches = []

        validator = CfnTemplateValidator({}).evolve(cfn=cfn)

        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self.schema,
            context=cfn.context,
        )

        matches.extend(self.json_schema_validate(cfn_validator, cfn.template, []))

        return matches
