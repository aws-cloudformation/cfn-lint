"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import template as schema_template
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class JsonSchema(BaseJsonSchema):
    """Check Base Template Settings"""

    id = "E1001"
    shortdesc = "Basic CloudFormation Template Configuration"
    description = (
        "Making sure the basic CloudFormation template components are properly"
        " configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["base"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "awsType": "E1100",
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
        self.validators["type"] = cfn_type
        self.config_definition = {"sections": {"default": "", "type": "string"}}
        self.configure()
        self.validators = {
            "awsType": None,
        }

    @property
    def schema(self):
        schema = load_resource(schema_template, "configuration.json")
        if self.config["sections"]:
            schema["properties"][self.config["sections"]] = True

        return schema

    def match(self, cfn):
        """Check CloudFormation Parameters"""
        matches = []

        cfn_validator = self.setup_validator(
            validator=CfnTemplateValidator,
            schema=self.schema,
            context=cfn.context.create_context_for_template(cfn.regions),
        ).evolve(
            cfn=cfn,
        )

        matches.extend(self.json_schema_validate(cfn_validator, cfn.template, []))

        return matches
