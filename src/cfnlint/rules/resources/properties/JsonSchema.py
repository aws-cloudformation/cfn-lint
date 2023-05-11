"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging

from cfnlint.helpers import REGION_PRIMARY
from cfnlint.rules.BaseJsonSchema import BaseJsonSchema
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
        self.validators = {
            "cfnRegionSchema": self._cfnRegionSchema,
        }
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
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.regions = [REGION_PRIMARY]

    def initialize(self, cfn):
        self.regions = cfn.regions
        return super().initialize(cfn)

    # pylint: disable=unused-argument
    def _cfnRegionSchema(self, validator, schema_paths, instance, schema):
        # when its the primary region we do this check once against
        # all regions
        if self.region != self.regions[0]:
            return
        if not self.child_rules.get("E3018"):
            return
        for region in self.regions:
            yield from self.child_rules.get("E3018").validate(
                validator,
                schema_paths,
                instance,
                schema,
                region,
            )

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
                        cfn_validator = self.setup_validator(schema=schema.json_schema)
                        path = ["Resources", n, "Properties"]
                        for scenario in cfn.get_object_without_nested_conditions(
                            p, path
                        ):
                            matches.extend(
                                self.json_schema_validate(
                                    cfn_validator, scenario.get("Object"), path
                                )
                            )

        return matches
