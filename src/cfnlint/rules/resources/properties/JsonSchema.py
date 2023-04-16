"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import re

import jsonschema
from jsonschema.exceptions import best_match

from cfnlint.helpers import (
    FN_PREFIX,
    PSEUDOPARAMS,
    REGEX_DYN_REF,
    REGION_PRIMARY,
    REGISTRY_SCHEMAS,
    UNCONVERTED_SUFFIXES,
    load_resource,
)
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import RuleMatch
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
            "cfnSchema": self._cfnSchema,
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

    # pylint: disable=unused-argument
    def _cfnSchema(self, validator, schema_paths, instance, schema, region=None):
        if isinstance(schema_paths, str):
            schema_paths = [schema_paths]

        for schema_path in schema_paths:
            schema_details = schema_path.split("/")
            cfn_schema = load_resource(
                f"cfnlint.data.schemas.extensions.{schema_details[0]}",
                filename=(f"{schema_details[1]}.json"),
            )
            cfn_validator = self.setup_validator(schema=cfn_schema)
            # cfn_validator = validator.evolve(schema=cfn_schema)
            errs = list(cfn_validator.iter_errors(instance))
            if errs:
                if cfn_schema.get("description"):
                    err = best_match(errs)
                    err.message = cfn_schema.get("description")
                    yield err
                else:
                    yield errs

    # pylint: disable=unused-argument
    def _cfnRegionSchema(self, validator, schema_paths, instance, schema):
        yield from self._cfnSchema(
            validator, schema_paths, instance, schema, self.region
        )

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for schema in REGISTRY_SCHEMAS:
            resource_type = schema["typeName"]
            for resource_name, resource_values in cfn.get_resources(
                [resource_type]
            ).items():
                properties = resource_values.get("Properties", {})
                # ignoring resources with CloudFormation template syntax in Properties
                if (
                    not re.match(REGEX_DYN_REF, str(properties))
                    and not any(
                        x in str(properties)
                        for x in PSEUDOPARAMS + UNCONVERTED_SUFFIXES
                    )
                    and FN_PREFIX not in str(properties)
                ):
                    try:
                        jsonschema.validate(properties, schema)
                    except ValidationError as e:
                        matches.append(
                            RuleMatch(
                                ["Resources", resource_name, "Properties"], e.message
                            )
                        )

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
                    if schema.json_schema():
                        if t in cached_validation_run or region == REGION_PRIMARY:
                            if schema.is_cached:
                                # if its cached we already ran the same validation lets not run it again
                                continue
                            cached_validation_run.append(t)
                        cfn_validator = self.setup_validator(
                            schema=schema.json_schema()
                        )
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
