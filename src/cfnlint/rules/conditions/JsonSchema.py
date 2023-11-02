"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import conditions as schema_conditions
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.jsonschema.base import BaseJsonSchema


class JsonSchema(BaseJsonSchema):
    """Check Conditions Configuration"""

    id = "E8000"
    shortdesc = "JSON Schema validation of Conditions section"
    description = (
        "Validate conditions in the Conditions section to make "
        "sure they are configured correctly"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html"
    tags = ["conditions"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "additionalProperties": "E8001",
            "maxProperties": "E8001",
            "patternProperties": "E8001",
            "type": "E8001",
            "awsType": "E8100",
            "fn_equals": "E8003",
            "fn_not": "E8005",
            "fn_and": "E8004",
            "fn_or": "E8006",
            "condition": "E8007",
            "ref": "E1020",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.schema = load_resource(schema_conditions, "conditions.json")

    def initialize(self, cfn):
        self.regions = cfn.regions
        return super().initialize(cfn)

    def match(self, cfn):
        """Check CloudFormation Outputs"""
        matches = []

        conditions = cfn.template.get("Conditions", {})

        cfn_validator = self.setup_validator(
            validator=CfnTemplateValidator,
            schema=self.schema,
            context=cfn.context.create_context_for_conditions(cfn.regions[0]),
        ).evolve(
            cfn=cfn,
        )

        matches.extend(
            self.json_schema_validate(cfn_validator, conditions, ["Conditions"])
        )

        return matches
