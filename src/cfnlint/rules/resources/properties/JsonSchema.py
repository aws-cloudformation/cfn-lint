"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import re
from copy import deepcopy
from typing import Any, Callable, Dict

import jsonschema

from cfnlint.helpers import (
    FN_PREFIX,
    PSEUDOPARAMS,
    REGEX_DYN_REF,
    REGISTRY_SCHEMAS,
    UNCONVERTED_SUFFIXES,
)
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema_manager import PROVIDER_SCHEMA_MANAGER
from cfnlint.template import Template

LOGGER = logging.getLogger("cfnlint.rules.resources.properties.JsonSchema")

# pylint: disable=too-many-instance-attributes
class RuleSet:
    def __init__(self):
        self.additionalProperties = "E3002"
        self.required = "E3003"
        self.enum = "E3030"
        self.type = "E3012"
        self.minLength = "E3033"
        self.maxLength = "E3033"
        self.uniqueItems = "E3037"
        self.maximum = "E3034"
        self.minimum = "E3034"
        self.exclusiveMaximum = "E3034"
        self.exclusiveMinimum = "E3034"
        self.maxItems = "E3032"
        self.minItems = "E3032"
        self.pattern = "E3031"
        self.oneOf = "E2523"


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
    }

    def __init__(self):
        """Init"""
        super().__init__()
        self.cfn = {}
        self.rules = RuleSet()
        self.config_definition = {"experimental": {"default": False, "type": "boolean"}}
        self.validator = None

    # pylint: disable=unused-argument
    def properties(self, validator, properties, instance, schema):
        if not validator.is_type(instance, "object"):
            return

        for p, subschema in properties.items():
            # use the instance keys because it gives us the start_mark
            k = [k for k in instance.keys() if k == p]
            if p in instance:
                yield from validator.descend(
                    instance[p],
                    subschema,
                    path=k[0] if len(k) > 0 else p,
                    schema_path=p,
                )

    def validate_additional_properties(self, validator, aP, instance, schema):
        if not validator.is_type(instance, "object"):
            return

        extras = set(find_additional_properties(instance, schema))

        if validator.is_type(aP, "object"):
            for extra in extras:
                yield from validator.descend(instance[extra], aP, path=extra)
        elif not aP and extras:
            if "patternProperties" in schema:
                if len(extras) == 1:
                    verb = "does"
                else:
                    verb = "do"

                joined = ", ".join(repr(each) for each in sorted(extras))
                patterns = ", ".join(
                    repr(each) for each in sorted(schema["patternProperties"])
                )
                error = f"{joined} {verb} not match any of the regexes: {patterns}"
                yield jsonschema.ValidationError(error)
            else:
                for extra in extras:
                    error = "Additional properties are not allowed (%s unexpected)"
                    yield jsonschema.ValidationError(error % extra, path=[extra])

    def json_schema_validate(self, validator, properties, path):
        matches = []
        for e in validator.iter_errors(properties):
            kwargs = {}
            if hasattr(e, "extra_args"):
                kwargs = getattr(e, "extra_args")
            if len(e.path) > 0:
                key = e.path[-1]
                if hasattr(key, "start_mark"):
                    kwargs["location"] = (
                        key.start_mark.line,
                        key.start_mark.column,
                        key.end_mark.line,
                        key.end_mark.column,
                    )
            matches.append(
                RuleMatch(
                    path + list(e.path),
                    e.message,
                    rule=self.child_rules[getattr(self.rules, e.validator)],
                    **kwargs,
                )
            )

        return matches

    def clense_schema(self, schema):
        """Taking a valid schema we will modify it for additional CloudFormation type things"""
        for ro_prop in schema.get("readOnlyProperties", []):
            sub_schema = schema
            for p in ro_prop.split("/")[1:-1]:
                sub_schema = sub_schema.get(p)
                if sub_schema is None:
                    break
            if sub_schema is not None:
                if sub_schema.get(ro_prop.split("/")[-1]) is not None:
                    del sub_schema[ro_prop.split("/")[-1]]

        return schema

    def _setup_validator(self, cfn: Template):
        validators: Dict[str, Callable[[Any, Any, Any, Any], Any]] = {
            "additionalProperties": self.validate_additional_properties,
            "properties": self.properties,
        }
        for js, rule_id in self.rules.__dict__.items():
            rule = self.child_rules.get(rule_id)
            if rule is not None:
                if hasattr(rule, "validate_configure") and callable(
                    getattr(rule, "validate_configure")
                ):
                    rule.validate_configure(cfn)
                if hasattr(rule, "validate") and callable(getattr(rule, "validate")):
                    validators[js] = rule.validate

        self.validator = jsonschema.validators.extend(
            jsonschema.Draft7Validator,
            validators=validators,
        )

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
                    except jsonschema.ValidationError as e:
                        matches.append(
                            RuleMatch(
                                ["Resources", resource_name, "Properties"], e.message
                            )
                        )

        if not self.config.get("experimental"):
            return matches

        self._setup_validator(cfn)

        for n, values in cfn.get_resources().items():
            p = values.get("Properties", {})
            t = values.get("Type", None)
            if t.startswith("Custom::"):
                t = "AWS::CloudFormation::CustomResource"
            if p and t:
                for region in cfn.regions:
                    schema = {}
                    try:
                        schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(region, t)
                    except FileNotFoundError as e:
                        if e.args[0] == region:
                            LOGGER.info("No specs for region %s", region)
                            continue
                    if schema:
                        schema = self.clense_schema(deepcopy(schema))
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


def find_additional_properties(instance, schema):
    """
    Return the set of additional properties for the given ``instance``.
    Weeds out properties that should have been validated by ``properties`` and
    / or ``patternProperties``.
    Assumes ``instance`` is dict-like already.
    """

    properties = schema.get("properties", {})
    patterns = "|".join(schema.get("patternProperties", {}))
    for p in instance:
        if p not in properties:
            if patterns and re.search(patterns, p):
                continue
            yield p
