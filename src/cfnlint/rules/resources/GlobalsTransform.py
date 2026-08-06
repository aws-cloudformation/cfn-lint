"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.sam
from cfnlint._typing import RuleMatches
from cfnlint.helpers import TRANSFORM_SAM, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules import RuleMatch
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails
from cfnlint.template import Template
from cfnlint.template.transforms._sam_globals import _GLOBALS_TYPE_MAP

# Reverse map: resource type -> Globals section key
_TYPE_TO_GLOBALS_MAP: dict[str, str] = {v: k for k, v in _GLOBALS_TYPE_MAP.items()}


def _is_intrinsic(value: Any) -> bool:
    """Check if value is a CloudFormation intrinsic function."""
    k, _ = is_function(value)
    return k is not None


class GlobalsTransform(CfnLintJsonSchema):
    """Check Globals section and validate IgnoreGlobals entries"""

    id = "E3724"
    shortdesc = "Validate Globals section and IgnoreGlobals entries"
    description = (
        "The Globals section is only valid in SAM templates. "
        "Check that the Serverless transform is declared, "
        "validate the Globals section structure, and verify that "
        "IgnoreGlobals entries reference valid global property names."
    )
    source_url = "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-template-anatomy-globals.html"
    tags = ["resources", "transform", "serverless"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Globals"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.sam, "globals.json"
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        """Validate the Globals section structure."""
        if not isinstance(instance, dict):
            return

        if not validator.cfn.has_serverless_transform():
            yield ValidationError(
                f"'Globals' section requires the serverless "
                f"transform {TRANSFORM_SAM!r}",
                rule=self,
            )
            return

        # Validate the Globals section structure against the schema
        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(),
        )
        yield from self._iter_errors(cfn_validator, instance)

    def match(self, cfn: Template) -> RuleMatches:
        """Validate IgnoreGlobals entries against actual Globals keys."""
        matches: RuleMatches = []

        # Only validate if SAM transform is present
        if not cfn.has_serverless_transform():
            return matches

        # Get the Globals section
        globals_section = cfn.template.get("Globals")
        if not isinstance(globals_section, dict):
            return matches

        # Skip if Globals contains intrinsics
        if _is_intrinsic(globals_section):
            return matches

        resources = cfn.template.get("Resources", {})
        if not isinstance(resources, dict):
            return matches

        # Check each resource's IgnoreGlobals
        for resource_name, resource in resources.items():
            if not isinstance(resource, dict):
                continue

            ignore_globals = resource.get("IgnoreGlobals")

            # IgnoreGlobals: "*" is always valid
            if ignore_globals == "*":
                continue

            # Must be a list to validate individual entries
            if not isinstance(ignore_globals, list):
                continue

            resource_type = resource.get("Type")
            if not isinstance(resource_type, str):
                continue

            # Find the corresponding Globals section key for this resource type
            globals_key = _TYPE_TO_GLOBALS_MAP.get(resource_type)
            if not globals_key:
                continue

            # Get the actual global properties for this resource type
            global_props = globals_section.get(globals_key)
            if not isinstance(global_props, dict):
                # No Globals defined for this resource type
                continue

            # Skip if global_props contains intrinsics
            if _is_intrinsic(global_props):
                continue

            valid_keys = set(global_props.keys())

            # Validate each entry in IgnoreGlobals
            for idx, entry in enumerate(ignore_globals):
                # Skip intrinsic function entries
                if _is_intrinsic(entry):
                    continue

                if not isinstance(entry, str):
                    continue

                if entry not in valid_keys:
                    path = ["Resources", resource_name, "IgnoreGlobals", idx]
                    message = (
                        f"{entry!r} is not a valid global property for "
                        f"{globals_key!r}. Valid properties are: "
                        f"{sorted(valid_keys)!r}"
                    )
                    matches.append(RuleMatch(path, message))

        return matches
