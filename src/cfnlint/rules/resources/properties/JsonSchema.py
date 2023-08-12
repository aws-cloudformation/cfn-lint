"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging

from cfnlint.context import create_context_for_resource_properties
from cfnlint.helpers import REGION_PRIMARY
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.jsonschema.base import BaseJsonSchema
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER, ResourceNotFoundError

LOGGER = logging.getLogger("cfnlint.rules.resources.properties.JsonSchema")


class JsonSchema(BaseJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3000"
    shortdesc = "Parent rule for doing JSON schema validation"
    description = "Making sure that resources properties comply with their JSON schema"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties"
    tags = ["resources"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "additionalProperties": "E3002",
            "properties": "E3002",
            "required": "E3003",
            "enum": "E3030",
            "type": "E3012",
            "minLength": "E3033",
            "maxLength": "E3033",
            "uniqueItems": "E3037",
            "maximum": "E3034",
            "minimum": "E3034",
            "exclusiveMaximum": "E3034",
            "exclusiveMinimum": "E3034",
            "maxItems": "E3032",
            "minItems": "E3032",
            "pattern": "E3031",
            "oneOf": "E2523",
            "awsType": "E3008",
            "cfnSchema": "E3017",
            "cfnRegionSchema": "E3018",
            "ref": "E1020",
            "fn_base64": "E1021",
            "fn_cidr": "E1012",
            "fn_findinmap": "E1011",
            "fn_foreach": "E1032",
            "fn_getatt": "E1010",
            "fn_getaz": "E1015",
            "fn_if": "E1014",
            "fn_importvalue": "E1015",
            "fn_join": "E1022",
            "fn_length": "E1030",
            "fn_select": "E1017",
            "fn_split": "E1018",
            "fn_sub": "E1019",
            "fn_tojsonstring": "E1031",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.regions = [REGION_PRIMARY]

    def initialize(self, cfn):
        self.regions = cfn.regions
        return super().initialize(cfn)

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for n, values in cfn.get_resources().items():
            p = values.get("Properties", {})
            t = values.get("Type", None)
            if t.startswith("Custom::"):
                t = "AWS::CloudFormation::CustomResource"
            if t:
                cached_validation_run = []
                for region in cfn.regions:
                    self.region = region
                    schema = {}
                    try:
                        schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(region, t)
                    except ResourceNotFoundError as e:
                        LOGGER.info(e)
                        continue
                    if schema.json_schema:
                        if t in cached_validation_run or region == REGION_PRIMARY:
                            if schema.is_cached:
                                # if its cached we already ran the
                                # same validation lets not run it again
                                continue
                            cached_validation_run.append(t)
                        cfn_validator = self.setup_validator(
                            validator=CfnTemplateValidator,
                            schema=schema.json_schema,
                            context=create_context_for_resource_properties(
                                cfn=cfn, region=region, resource_name=n
                            ),
                        ).evolve(
                            cfn=cfn,
                        )
                        path = ["Resources", n, "Properties"]
                        matches.extend(
                            self.json_schema_validate(cfn_validator, p, path)
                        )

        return matches
