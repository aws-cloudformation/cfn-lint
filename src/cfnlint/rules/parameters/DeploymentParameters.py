"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class DeploymentParameters(CfnLintJsonSchema):
    """Check if Parameters are configured correctly"""

    id = "E2900"
    shortdesc = (
        "Validate deployment file parameters are valid against template parameters"
    )
    description = (
        "Validates that required properties are provided, allowed values are "
        "valid, types are correct, and the pattern matches in a deployment file "
        "for the parameters specified in a template"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html"
    tags = ["parameters"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Parameters"],
            all_matches=True,
        )

    def _is_type_a_list(self, parameter_type: str) -> bool:
        return "List" in parameter_type and "CommaDelimitedList" not in parameter_type

    def _build_schema(self, instance: Any) -> dict[str, Any]:
        if not isinstance(instance, dict):
            return {}

        schema: dict[str, Any] = {
            "properties": {},
            "additionalProperties": False,
            "required": [],
            "type": "object",
        }

        singular_types = ["string", "integer", "number", "boolean"]

        for parameter_name, parameter_object in instance.items():
            schema["properties"][parameter_name] = {}
            if not isinstance(parameter_object, dict):
                continue
            if "Default" not in parameter_object:
                schema["required"] = [parameter_name]

            parameter_type = parameter_object.get("Type")
            if not isinstance(parameter_type, str):
                continue

            if self._is_type_a_list(parameter_type):
                schema["properties"][parameter_name] = {
                    "type": "array",
                    "items": {
                        "type": singular_types,
                    },
                }
                if "AllowedValues" in parameter_object:
                    schema["properties"][parameter_name]["items"]["enum"] = (
                        parameter_object["AllowedValues"]
                    )
                if "Pattern" in parameter_object:
                    if self._is_type_a_list(parameter_type):
                        schema["properties"][parameter_name]["items"]["pattern"] = (
                            parameter_object["Pattern"]
                        )
            else:
                schema["properties"][parameter_name]["type"] = singular_types
                if "AllowedValues" in parameter_object:
                    schema["properties"][parameter_name]["enum"] = parameter_object[
                        "AllowedValues"
                    ]
                if "Pattern" in parameter_object:
                    schema["properties"][parameter_name]["pattern"] = parameter_object[
                        "Pattern"
                    ]

        return schema

    def validate(self, validator: Validator, _: Any, instance: Any, schema: Any):
        if not validator.cfn.parameters:
            return

        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._build_schema(instance),
            context=validator.context,
        ).evolve(
            context=validator.context.evolve(strict_types=False),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
        )

        for err in super()._iter_errors(cfn_validator, validator.cfn.parameters):
            # we use enum twice.  Once for the type and once for the property
            # names.  There are separate error numbers so we do this.
            if "propertyNames" in err.schema_path and "enum" in err.schema_path:
                err.rule = self
            yield err
