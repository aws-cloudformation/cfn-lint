"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import re

import jsonschema

from cfnlint.helpers import (
    FN_PREFIX,
    PSEUDOPARAMS,
    REGEX_DYN_REF,
    REGISTRY_SCHEMAS,
    UNCONVERTED_SUFFIXES,
    load_resource,
)
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema.validator import create as create_validator
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER, ResourceNotFoundError
from cfnlint.template.template import Template

LOGGER = logging.getLogger("cfnlint.rules.resources.properties.JsonSchema")


_rule_set = {
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
}


class JsonSchema(CloudFormationLintRule):
    """Check Base Resource Configuration"""

    id = "E3000"
    shortdesc = "Parent rule for doing JSON schema validation"
    description = "Making sure that resources properties comply with their JSON schema"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties"
    tags = ["resources"]
    child_rules = {
        "E2523": None,
        "E3002": None,
        "E3003": None,
        "E3012": None,
        "E3030": None,
        "E3031": None,
        "E3032": None,
        "E3033": None,
        "E3034": None,
        "E3037": None,
        "E3008": None,
        "E3017": None,
    }

    def __init__(self):
        """Init"""
        super().__init__()
        self.cfn = {}
        self.validator = None
        self.rules = {}
        for name, _ in _rule_set.items():
            self.rules[name] = None

    def json_schema_validate(self, validator, properties, path):
        matches = []
        for e in validator.iter_errors(properties):
            kwargs = {}
            if hasattr(e, "extra_args"):
                kwargs = getattr(e, "extra_args")
            e_path = path + list(e.path)
            if len(e.path) > 0:
                e_path_override = getattr(e, "path_override", None)
                if e_path_override:
                    e_path = list(e.path_override)
                else:
                    key = e.path[-1]
                    if hasattr(key, "start_mark"):
                        kwargs["location"] = (
                            key.start_mark.line,
                            key.start_mark.column,
                            key.end_mark.line,
                            key.end_mark.column,
                        )

            e_rule = None
            if hasattr(e, "rule"):
                if e.rule:
                    e_rule = e.rule
            if not e_rule:
                e_rule = self.rules.get(e.validator, self)

            matches.append(
                RuleMatch(
                    e_path,
                    e.message,
                    rule=e_rule,
                    **kwargs,
                )
            )

        return matches

    def _setup_validator(self, cfn: Template):
        for name, rule_id in _rule_set.items():
            self.rules[name] = self.child_rules.get(rule_id)

        self.validator = create_validator(
            validators={
                "awsType": None,
                "cfnSchema": self._cfnSchema,
            },
            cfn=cfn,
            rules=self.rules,
        )

    # pylint: disable=unused-argument
    def _cfnSchema(self, validator, schema_paths, instance, schema):
        if isinstance(schema_paths, str):
            schema_paths = [schema_paths]

        for schema_path in schema_paths:
            schema_details = schema_path.split("/")
            cfn_schema = load_resource(
                f"cfnlint.data.AdditionalSchemas.{schema_details[0]}",
                filename=(f"{schema_details[1]}.json"),
            )
            cfn_validator = self.validator(cfn_schema)
            if cfn_schema.get("description"):
                if not cfn_validator.is_valid(instance):
                    yield ValidationError(cfn_schema.get("description"))
            else:
                yield from cfn_validator.iter_errors(instance)

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = []
        self.cfn = cfn

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

        self._setup_validator(cfn=cfn)

        for n, values in cfn.get_resources().items():
            p = values.get("Properties", {})
            t = values.get("Type", None)
            if t.startswith("Custom::"):
                t = "AWS::CloudFormation::CustomResource"
            if t:
                for region in cfn.regions:
                    schema = {}
                    try:
                        schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(
                            region, t
                        ).json_schema()
                    except ResourceNotFoundError as e:
                        LOGGER.info(e)
                        continue
                    if schema:
                        cfn_validator = self.validator(schema)
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
