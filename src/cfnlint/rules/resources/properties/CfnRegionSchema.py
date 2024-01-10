"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import pathlib
from typing import Sequence

from cfnlint.helpers import load_plugins, load_resource
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.jsonschema._utils import Unset
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.base import BaseJsonSchema


class CfnRegionSchema(BaseJsonSchema):
    """Check additional schemas against a set of by regoin"""

    id = "E3018"
    shortdesc = "Properties are validated against additional schemas based on region"
    description = (
        "Use supplemental regional JSON schemas to validate properties against"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__()
        root_dir = pathlib.Path(__file__).parent.parent
        rules = load_plugins(
            str(root_dir),
            "BaseCfnRegionSchema",
            "cfnlint.rules.resources.properties.CfnRegionSchema",
        )
        for rule in rules:
            self.child_rules[rule.id] = rule
        self.regions: Sequence[str] = []

    # pylint: disable=unused-argument
    def cfnRegionSchema(self, validator, schema_paths, instance, schema):
        if isinstance(schema_paths, str):
            schema_paths = [schema_paths]

        for schema_path in schema_paths:
            for rule in self.child_rules.values():
                if rule.schema_path == schema_path:
                    yield from rule.validate(
                        validator, instance, validator.context.regions
                    )


class BaseCfnRegionSchema(BaseJsonSchema):
    """Check additional schemas against a set of properties
    for a region
    """

    schema_path = ""

    def __init__(self) -> None:
        super().__init__()
        schema_split = self.schema_path.split("/")
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
        if len(schema_split) > 1:
            self.cfn_schema = load_resource(
                f"cfnlint.data.schemas.extensions.{schema_split[0]}",
                filename=(f"{schema_split[1]}.json"),
            )
            self.cfn_validator = None

    def validate(self, validator, instance, regions):
        # if the schema has a description will only replace the message with that
        # description and use the best error for the location information
        for region in regions:
            self.cfn_validator = self.setup_validator(
                validator=CfnTemplateValidator,
                schema=self.cfn_schema.get(region, {}),
                context=validator.context.evolve(),
            )
            err = best_match(list(self.cfn_validator.iter_errors(instance)))
            if err is not None:
                yield ValidationError(
                    message=f"{err.message} in {region}",
                    validator=err.validator,
                    path=err.path,
                    cause=err.cause,
                    context=err.context,
                    validator_value=err.validator_value,
                    instance=err.instance,
                    schema=err.schema,
                    schema_path=err.schema_path,
                    parent=err.parent,
                    type_checker=err.type_check
                    if hasattr(err, "type_check")
                    else Unset(),
                    rule=self,
                )
