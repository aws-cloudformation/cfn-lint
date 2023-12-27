"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import pathlib

from cfnlint.helpers import load_plugins, load_resource
from cfnlint.jsonschema import StandardValidator
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.base import BaseJsonSchema


class CfnSchema(BaseJsonSchema):
    id = "E3017"
    shortdesc = "Properties are validated against additional schemas"
    description = "Use supplemental JSON schemas to validate properties against"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__()
        root_dir = pathlib.Path(__file__).parent.parent
        rules = load_plugins(
            str(root_dir),
            "BaseCfnSchema",
            "cfnlint.rules.resources.properties.CfnSchema",
        )
        for rule in rules:
            self.child_rules[rule.id] = rule

    # pylint: disable=unused-argument
    def cfnSchema(self, validator, schema_paths, instance, schema, region=None):
        if isinstance(schema_paths, str):
            schema_paths = [schema_paths]

        for schema_path in schema_paths:
            for rule in self.child_rules.values():
                if rule.schema_path == schema_path:
                    yield from rule.validate(validator, instance)


class BaseCfnSchema(BaseJsonSchema):
    schema_path = ""
    all_matches = False

    def __init__(self) -> None:
        super().__init__()
        schema_split = self.schema_path.split("/")
        if len(schema_split) > 1:
            self.cfn_schema = load_resource(
                f"cfnlint.data.schemas.extensions.{schema_split[0]}",
                filename=(f"{schema_split[1]}.json"),
            )

    def validate(self, validator, instance):
        # if the schema has a description will only replace the message with that
        # description and use the best error for the location information
        cfn_validator = self.setup_validator(
            validator=StandardValidator,
            schema=self.cfn_schema,
            context=validator.context.evolve(),
        )

        errs = list(cfn_validator.iter_errors(instance))
        if not self.all_matches:
            err = best_match(errs)
            if err is not None:
                err.message = self.shortdesc
                err.rule = self
                errs = [err]

        yield from iter(errs)
