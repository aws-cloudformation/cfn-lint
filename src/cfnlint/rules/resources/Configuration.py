"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.helpers
from cfnlint.data.schemas.other import resources
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.jsonschema.base import BaseJsonSchema
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER


class Configuration(BaseJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3001"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__()
        self.schema = cfnlint.helpers.load_resource(resources, "configuration.json")
        self.regions = []
        self.cfn = None
        self.validators = {
            "awsType": self.awsType,
        }
        self.rule_set = {
            "fn_base64": "E1021",
            "fn_cidr": "E1012",
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
        self.child_rules["E3009"] = None
        self.types = {
            "CfnInit": "E3009",
        }

    def initialize(self, cfn):
        super().initialize(cfn)
        self.regions = cfn.regions
        self.cfn = cfn

    # pylint: disable=unused-argument
    def awsType(self, validator, iT, instance, schema):
        if validator.is_type(iT, "string") and iT.startswith("CfnInit"):
            rule = self.child_rules.get(self.types.get("CfnInit", ""))
            if not rule:
                return

            if hasattr(rule, iT.lower()) and callable(getattr(rule, iT.lower())):
                validate = getattr(rule, iT.lower())
                for err in validate(validator, iT, instance, schema):
                    yield err

            return

        resource_type = instance.get("Type")
        if not validator.is_type(resource_type, "string"):
            return

        resource_condition = instance.get("Condition")

        for region in self.regions:
            if validator.is_type(resource_condition, "string"):
                if False in self.cfn.conditions.build_scenerios_on_region(
                    resource_condition, region
                ):
                    continue
            if resource_type in PROVIDER_SCHEMA_MANAGER.get_resource_types(
                region=region
            ):
                continue
            if not resource_type.startswith(
                ("Custom::", "AWS::Serverless::")
            ) and not resource_type.endswith("::MODULE"):
                yield ValidationError(
                    f"Resource type `{resource_type}` does not exist in '{region}'"
                )

    def match(self, cfn):
        matches = []

        resources = cfn.template.get("Resources", {})
        validator = self.setup_validator(
            CfnTemplateValidator,
            self.schema,
            context=cfn.context.create_context_for_resources(cfn.regions[0]),
        )

        matches.extend(self.json_schema_validate(validator, resources, ["Resources"]))

        return matches
