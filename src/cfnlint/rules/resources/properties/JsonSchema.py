"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging

from cfnlint.context import Context
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
            # properties
            "additionalProperties": "E3002",
            "properties": "E3002",
            "required": "E3003",
            "minProperties": "E3002",
            "maxProperties": "E3002",
            # array
            "maxItems": "E3032",
            "minItems": "E3032",
            "uniqueItems": "E3037",
            # generic
            "enum": "E3030",
            # type
            "type": "E3012",
            # string
            "minLength": "E3033",
            "maxLength": "E3033",
            "pattern": "E3031",
            # number
            "maximum": "E3034",
            "minimum": "E3034",
            "exclusiveMaximum": "E3034",
            "exclusiveMinimum": "E3034",
            # composition
            "oneOf": "E2523",
            "anyOf": "E2522",
            # cfn-lint additions
            "awsType": "E3008",
            "cfnSchema": "E3017",
            "cfnRegionSchema": "E3018",
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
                        ).evolve(context=Context(region), cfn=cfn)
                        path = ["Resources", n, "Properties"]
                        matches.extend(
                            self.json_schema_validate(cfn_validator, p, path)
                        )

        return matches
