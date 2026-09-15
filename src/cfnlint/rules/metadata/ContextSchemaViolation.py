"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.metadata
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import StandardValidator
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.rules.metadata._BaseContext import (
    _CONTEXT_DISPLAY,
    CONTEXT_KEY,
    CONTEXT_SCHEMA_URL,
    ContextRuleMixin,
    _get_context,
)

_SCHEMA = load_resource(cfnlint.data.schemas.other.metadata, "context.json")
_RESOURCE_FIELDS = frozenset(_SCHEMA["definitions"]["ResourceContext"]["properties"])
_TEMPLATE_FIELDS = frozenset(_SCHEMA["definitions"]["TemplateContext"]["properties"])
_TEMPLATE_ONLY_FIELDS = _TEMPLATE_FIELDS - _RESOURCE_FIELDS
_RESOURCE_ONLY_FIELDS = _RESOURCE_FIELDS - _TEMPLATE_FIELDS
_TEMPLATE_FIELDS_STR = ", ".join(sorted(_TEMPLATE_FIELDS))
_RESOURCE_FIELDS_STR = ", ".join(sorted(_RESOURCE_FIELDS))


def _get_subschema(def_name: str) -> dict[str, Any]:
    """Resolve a definitions entry into a standalone schema for $ref."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": _SCHEMA["definitions"],
        "$ref": f"#/definitions/{def_name}",
    }


_VALIDATORS: dict[str, StandardValidator] = {
    "ResourceContext": StandardValidator(_get_subschema("ResourceContext")),
    "TemplateContext": StandardValidator(_get_subschema("TemplateContext")),
}

_MSG_NOT_A_MAPPING = (
    "{location}: 'Context' does not match expected shape. Expected a mapping of "
    "Context fields, got a scalar/list. Fix the field to match the expected "
    "shape: object."
)
_MSG_MISPLACED_FIELD = (
    "{location}: '{key}' belongs at {correct_level} level. Move the field to the "
    "correct level. Template level: {template_fields}. Resource level: "
    "{resource_fields}."
)
_MSG_UNRECOGNIZED_FIELD = (
    "{location}: '{key}' is not a recognized Context field. Remove it or use one "
    "of: {allowed}."
)
_MSG_ENUM_VALUE = (
    "{location}: '{field}' value '{instance}' is not a recognized value. Use one "
    "of the allowed values: {allowed_values}."
)
_MSG_WRONG_SHAPE = (
    "{location}: '{field}' does not match expected shape. {detail}. Fix the field "
    "to match the expected shape: {expected}."
)


def _expected_shape(field: str, placement_def: str) -> str:
    """Compact human description of a field's expected shape, from the schema."""
    prop = _SCHEMA["definitions"][placement_def]["properties"].get(field, {})
    ref = prop.get("$ref", "")
    if ref.endswith("TrustObject"):
        return "object with required 'src' and 'conf'"
    if ref.endswith("MutabilityLevel"):
        return "one of: " + ", ".join(_SCHEMA["definitions"]["MutabilityLevel"]["enum"])
    schema_type = prop.get("type")
    if schema_type == "array":
        items = prop.get("items", {})
        items_ref = items.get("$ref", "")
        if items_ref.endswith("RefEntry"):
            return (
                "array of ref entries (each a URI string or {at, has?, scope?} object)"
            )
        return "array of strings"
    if schema_type == "object":
        return "mapping of property name to mutability level"
    if schema_type == "string":
        return "string"
    # Unreachable for the current schema; every field above is covered. Kept so
    # a field added later degrades to a usable message instead of a KeyError.
    return f"see the '{field}' definition in the Context schema"


class _Finding:
    """A schema-validation finding: where it occurred and the message."""

    def __init__(self, path: list[Any], message: str) -> None:
        self.path = path
        self.message = message


def _schema_findings(
    block: Any, placement_def: str, base_path: list[Any], location: str
) -> list[_Finding]:
    """Validate one Context block against its placement sub-schema.

    ``location`` is the diagnostic's ``<Resource>`` label (a logical ID, or
    "Template" for the template-level block).

    Reports each problem with a specific message: fields on the wrong placement
    level, enum fields with an unrecognized value, and type/shape or
    unrecognized-field problems.
    """
    findings: list[_Finding] = []

    if not isinstance(block, dict):
        findings.append(
            _Finding(base_path, _MSG_NOT_A_MAPPING.format(location=location))
        )
        return findings

    # Top-level unknown keys: split misplaced (wrong level) from unrecognized.
    allowed = (
        _RESOURCE_FIELDS if placement_def == "ResourceContext" else _TEMPLATE_FIELDS
    )
    misplaced_pool = (
        _TEMPLATE_ONLY_FIELDS
        if placement_def == "ResourceContext"
        else _RESOURCE_ONLY_FIELDS
    )
    correct_level = "template" if placement_def == "ResourceContext" else "resource"
    for key in block:
        if key in allowed:
            continue
        if key in misplaced_pool:
            findings.append(
                _Finding(
                    base_path + [key],
                    _MSG_MISPLACED_FIELD.format(
                        location=location,
                        key=key,
                        correct_level=correct_level,
                        template_fields=_TEMPLATE_FIELDS_STR,
                        resource_fields=_RESOURCE_FIELDS_STR,
                    ),
                )
            )
        else:
            findings.append(
                _Finding(
                    base_path + [key],
                    _MSG_UNRECOGNIZED_FIELD.format(
                        location=location,
                        key=key,
                        allowed=", ".join(sorted(allowed)),
                    ),
                )
            )

    validator = _VALIDATORS[placement_def]
    for error in sorted(
        validator.iter_errors(block), key=lambda e: list(e.absolute_path)
    ):
        err_path = list(error.absolute_path)
        # Top-level unknown keys are reported above; the validator puts the
        # offending key at path length 1. Nested ones are real shape problems.
        if error.validator == "additionalProperties" and len(err_path) <= 1:
            continue
        field = ".".join(str(p) for p in err_path) or "Context"
        top_field = str(err_path[0]) if err_path else field
        if error.validator == "enum":
            allowed_values = ", ".join(str(v) for v in error.validator_value)
            findings.append(
                _Finding(
                    base_path + err_path,
                    _MSG_ENUM_VALUE.format(
                        location=location,
                        field=field,
                        instance=error.instance,
                        allowed_values=allowed_values,
                    ),
                )
            )
        else:
            findings.append(
                _Finding(
                    base_path + err_path,
                    _MSG_WRONG_SHAPE.format(
                        location=location,
                        field=field,
                        detail=error.message,
                        expected=_expected_shape(top_field, placement_def),
                    ),
                )
            )
    return findings


class ContextSchemaViolation(ContextRuleMixin, CloudFormationLintRule):
    """schema-violation: a supplied Context block fails schema v1 validation."""

    id = "W4012"
    experimental = True
    shortdesc = "Context field does not match the schema"
    description = (
        f"Check a supplied {_CONTEXT_DISPLAY} block against"
        " the Context schema: field types and shapes, recognized enum values,"
        " and fields placed at the correct level (template fields on the"
        " template, resource fields on resources)."
    )
    source_url = CONTEXT_SCHEMA_URL
    tags = ["metadata", "context"]

    def match(self, cfn: Any) -> list[RuleMatch]:
        if self._is_cdk_template(cfn):
            return []
        return self._schema_matches(cfn)

    def _schema_matches(self, cfn: Any) -> list[RuleMatch]:
        """RuleMatches for every schema violation across all Context blocks."""
        matches = []
        for logical_id, resource in self._primary_resources(cfn):
            context = _get_context(resource)
            if context is None:
                continue
            base_path = ["Resources", logical_id, "Metadata", CONTEXT_KEY]
            for finding in _schema_findings(
                context, "ResourceContext", base_path, logical_id
            ):
                matches.append(RuleMatch(finding.path, finding.message))
        template_metadata = cfn.template.get("Metadata")
        if isinstance(template_metadata, dict) and CONTEXT_KEY in template_metadata:
            context = template_metadata[CONTEXT_KEY]
            for finding in _schema_findings(
                context, "TemplateContext", ["Metadata", CONTEXT_KEY], "Template"
            ):
                matches.append(RuleMatch(finding.path, finding.message))
        return matches
