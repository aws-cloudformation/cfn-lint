"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import pathlib

from jsonschema.exceptions import best_match

from cfnlint.helpers import load_plugins, load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._utils import Unset
from cfnlint.rules.BaseJsonSchema import BaseJsonSchema


class CfnSchema(BaseJsonSchema):
    id = "E3017"
    shortdesc = "Properties are validated against additional schemas"
    description = "Use supplemental JSON schemas to validate properties against"
    tags = ["resources"]

    def __init__(self) -> None:
        root_dir = pathlib.Path(__file__).parent.parent
        rules = load_plugins(
            str(root_dir),
            "BaseCfnSchema",
            "cfnlint.rules.resources.properties.CfnSchema",
        )
        for rule in rules:
            self.child_rules[rule.id] = rule
        super().__init__()

    # pylint: disable=unused-argument
    def cfnSchema(self, validator, schema_paths, instance, schema, region=None):
        if isinstance(schema_paths, str):
            schema_paths = [schema_paths]

        for schema_path in schema_paths:
            for rule in self.child_rules.values():
                if rule.schema_path == schema_path:
                    yield from rule.validate(instance)


class BaseCfnSchema(BaseJsonSchema):
    schema_path = ""

    def __init__(self) -> None:
        super().__init__()
        schema_split = self.schema_path.split("/")
        if len(schema_split) > 1:
            self.cfn_schema = load_resource(
                f"cfnlint.data.schemas.extensions.{schema_split[0]}",
                filename=(f"{schema_split[1]}.json"),
            )
            self.cfn_validator = self.setup_validator(schema=self.cfn_schema)

    def validate(self, instance):
        # if the schema has a description will only replace the message with that
        # description and use the best error for the location information
        err = best_match(list(self.cfn_validator.iter_errors(instance)))
        if err is not None:
            yield ValidationError(
                message=self.shortdesc,
                validator=err.validator,
                path=err.path,
                cause=err.cause,
                context=err.context,
                validator_value=err.validator_value,
                instance=err.instance,
                schema=err.schema,
                schema_path=err.schema_path,
                parent=err.parent,
                type_checker=err.type_check if hasattr(err, "type_check") else Unset(),
                rule=self,
            )
