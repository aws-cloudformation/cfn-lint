"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

# cfn-lint rules for CloudFormation Metadata.com.aws.cloudformation.Context blocks.
#
# The Context convention lets templates carry design rationale in metadata: a
# top-level architecture summary plus per-resource "why / must / mutability"
# notes (emitted by the CDK context aspect, aws/aws-cdk#38381). These rules
# implement the Context family on the cfn-lint surface:
#
#   W4010 missing-context    Template or significant resource has no Context block
#   W4011 missing-why        Context present but has neither 'why' nor 'gaps'
#   W4012 schema-violation   Supplied Context field fails schema v1 validation
#
# All rules are warnings (advisory, never blocking). Each accepts a 'severity'
# config option (--configure-rule W4010:severity=error) so CI can escalate.
#
# missing-context (W4010) is OFF by default -- *requiring* a Context block is a
# team policy choice, so enable it with --configure-rule W4010:require_context=true.
# The validate-supplied rules (W4011, W4012) are on by default but only fire when
# an author has actually written a Context block, so they are silent otherwise.
#
# Targeting follows a shared exclusion set: incidental/framework resources
# (matched against the canonical incidental pattern set on logical IDs and the
# aws:cdk:path metadata value) are never flagged. Authors opt out per resource
# with gaps: [context intentionally omitted] or cfn-lint's native suppression,
# and can extend the incidental set via the additional_incidental_patterns
# config option.
#
# missing-context (W4010) additionally applies a significance policy: only
# resources *required* to carry context are flagged when it is absent.
# Subordinate / low-value resource types (e.g. AWS::Logs::LogGroup) are not
# required and are skipped by W4010, but any context an author does supply is
# still validated by W4011-W4012. Extend the low-value set via the
# additional_low_value_types config option. W4010 also flags a template that has
# more than one significant resource but whose top-level Metadata has no Context
# block describing its architecture.

from __future__ import annotations

import re
from typing import Any

import cfnlint.data.schemas.other.metadata
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import StandardValidator
from cfnlint.rules import CloudFormationLintRule, RuleMatch

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# Canonical location of the Context block (aws/aws-cdk#38381).
CONTEXT_KEY = "com.aws.cloudformation.Context"

# Human-facing display of the block's location. Dotted form matches the
# production diagnostic copy validated by the W9100 benchmark.
_CONTEXT_DISPLAY = "Metadata.com.aws.cloudformation.Context"

_SCHEMA = load_resource(cfnlint.data.schemas.other.metadata, "context.json")
_RESOURCE_FIELDS = frozenset(_SCHEMA["definitions"]["ResourceContext"]["properties"])
_TEMPLATE_FIELDS = frozenset(_SCHEMA["definitions"]["TemplateContext"]["properties"])
_TEMPLATE_ONLY_FIELDS = _TEMPLATE_FIELDS - _RESOURCE_FIELDS
_RESOURCE_ONLY_FIELDS = _RESOURCE_FIELDS - _TEMPLATE_FIELDS


def _get_subschema(def_name: str) -> dict[str, Any]:
    """Resolve a definitions entry into a standalone schema for $ref."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": _SCHEMA["definitions"],
        "$ref": f"#/definitions/{def_name}",
    }


# Pre-built validators (one per placement level -- schemas are static for the module).
_VALIDATORS: dict[str, StandardValidator] = {
    "ResourceContext": StandardValidator(_get_subschema("ResourceContext")),
    "TemplateContext": StandardValidator(_get_subschema("TemplateContext")),
}

# Canonical incidental pattern set: generated helper resources emitted by the
# CDK context aspect (log-retention custom resources, provider framework
# handlers). These are never flagged.
#
# For aws:cdk:path values, patterns are matched per path segment where
# ambiguity exists (Provider) or as substrings where the token is unique
# enough (LogRetention, framework-*, AWS679...). For bare logical IDs, we
# anchor patterns to avoid false positives like "DataProviderTable".
_INCIDENTAL_PATH_PATTERN = re.compile(
    r"LogRetention|(?:^|/)Provider(?:/|$)|framework-onEvent|framework-isComplete"
    r"|framework-onTimeout|AWS679f53fac002430cb0da5b7982bd2287"
)
_INCIDENTAL_ID_PATTERN = re.compile(
    r"^LogRetention|(?<=[a-z])Provider(?=framework)"
    r"|frameworkonEvent|frameworkisComplete"
    r"|frameworkonTimeout|^AWS679f53fac002430cb0da5b7982bd2287$"
)
_CDK_METADATA_TYPE = "AWS::CDK::Metadata"
_CDK_METADATA_LOGICAL_ID = "CDKMetadata"
_CDK_PATH_KEY = "aws:cdk:path"

# Per-resource opt-out marker.
_OPT_OUT_MARKER = "context intentionally omitted"

# Resource types not *required* to carry context: subordinate / low-value
# resources near-universally attached to a parent (e.g. a function's log group)
# rather than independently architecture-relevant. Missing context is NOT flagged
# on these (W4010); any context an author supplies is still validated
# (W4011-W4012). Extend via the 'additional_low_value_types' config option.
#
# Significance-policy choice (W9100 benchmark): the benchmark offered two LogGroup
# policies -- (a) exempt every AWS::Logs::LogGroup by type, or (b) exempt only
# mechanically-subordinate LogGroups while still requiring context on
# independently-significant audit/logging groups. This rule takes (a) for a low
# false-positive rate. Tradeoff: a genuinely standalone audit LogGroup is also
# exempted from the requirement (its supplied context is still validated). Revisit
# with subordinate-detection if standalone logging resources must be covered.
_LOW_VALUE_TYPES = frozenset(
    {
        "AWS::Logs::LogGroup",
        "AWS::Logs::LogStream",
    }
)

_VALID_SEVERITIES = frozenset({"error", "warning", "informational"})
_DEFAULT_SEVERITY = "warning"

_SEVERITY_CONFIG: dict[str, Any] = {"default": _DEFAULT_SEVERITY, "type": "string"}
_PATTERNS_CONFIG: dict[str, Any] = {"default": [], "type": "list", "itemtype": "string"}


# ---------------------------------------------------------------------------
# Shared helpers (module-level so the mixin below stays stateless)
# ---------------------------------------------------------------------------


def _is_incidental(
    logical_id: str, resource: dict[str, Any], extra_patterns: list[str]
) -> bool:
    """True when the resource is incidental/framework per the targeting policy."""
    if resource.get("Type") == _CDK_METADATA_TYPE:
        return True
    if logical_id == _CDK_METADATA_LOGICAL_ID:
        return True
    metadata = resource.get("Metadata")
    cdk_path = metadata.get(_CDK_PATH_KEY) if isinstance(metadata, dict) else None
    # Logical ID: anchored pattern to avoid false positives (e.g. DataProviderTable).
    if _INCIDENTAL_ID_PATTERN.search(logical_id):
        return True
    # aws:cdk:path: segment-bounded for Provider, substring for unique tokens.
    if cdk_path and _INCIDENTAL_PATH_PATTERN.search(str(cdk_path)):
        return True
    # User-configured extra patterns: applied to both logical ID and cdk path.
    candidates = [logical_id] + ([str(cdk_path)] if cdk_path else [])
    for pattern in extra_patterns:
        for candidate in candidates:
            try:
                if re.search(pattern, candidate):
                    return True
            except re.error:
                continue
    return False


def _is_low_value(resource: dict[str, Any], extra_types: list[str]) -> bool:
    """True when the resource's type is subordinate/low-value.

    Low-value resources are not *required* to carry context (missing-context is
    suppressed by W4010), but any context they supply is still validated.
    """
    rtype = resource.get("Type")
    if not isinstance(rtype, str):
        return False
    return rtype in _LOW_VALUE_TYPES or rtype in extra_types


def _get_context(resource: dict[str, Any]) -> Any:
    """Return the resource's Context metadata block (any shape), or None."""
    metadata = resource.get("Metadata")
    if not isinstance(metadata, dict):
        return None
    return metadata.get(CONTEXT_KEY)


def _is_opted_out(context: Any) -> bool:
    """True when the block carries the explicit per-resource opt-out marker.

    Matching is case-insensitive and substring-based, so variations like
    "Context Intentionally Omitted (JIRA-123)" are accepted.
    """
    if not isinstance(context, dict):
        return False
    gaps = context.get("gaps")
    if not isinstance(gaps, list):
        return False
    return any(isinstance(gap, str) and _OPT_OUT_MARKER in gap.lower() for gap in gaps)


# ---------------------------------------------------------------------------
# Diagnostic message templates. Named so the wording lives in one place, apart
# from the detection logic, and is easy to review. Runtime values are filled in
# with str.format(); {context_display} is the dotted Metadata path and field
# lists come from the schema. Fully-static messages are baked with f-strings.
# ---------------------------------------------------------------------------
_TEMPLATE_FIELDS_STR = ", ".join(sorted(_TEMPLATE_FIELDS))
_RESOURCE_FIELDS_STR = ", ".join(sorted(_RESOURCE_FIELDS))

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
_MSG_TEMPLATE_MISSING = (
    f"This template is missing a top-level {_CONTEXT_DISPLAY} block describing its "
    f"architecture. Add top-level {_CONTEXT_DISPLAY} and set 'arch' to a concise "
    "summary of the template's high-level resource and data flow. Add 'must' as a "
    "list only for known cross-cutting constraints; otherwise omit it. Do not "
    "guess or invent constraints."
)
_MSG_CHILD_MISSING = f"This resource is missing {_CONTEXT_DISPLAY}."
_MSG_RESOURCE_AGGREGATE = (
    "These architecture-relevant resources are missing {context_display}: "
    "{summary}. For each listed resource, add {context_display}. Set 'why' to the "
    "resource's purpose or design rationale. If the rationale is not documented, "
    "set 'gaps' to [\"rationale not documented\"] instead of guessing. Add "
    "'must' as a list only for known constraints whose violation would break the "
    "system; otherwise omit it. Leave unlisted resources unchanged."
)
_MSG_MISSING_WHY = (
    "{logical_id}: {context_display} has no 'why'. Add 'why': purpose + notable "
    'choices, telegraphic style (e.g. "buffer order events async; FIFO rejected '
    '(throughput > ordering)") -- or declare gaps: [rationale not documented]. '
    "Never restate the Type/logical id/property values."
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
    return "see the Context schema v1"


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

    # Field-level validation for known fields (skip top-level additionalProperties --
    # handled above; nested additionalProperties are genuine shape problems).
    validator = _VALIDATORS[placement_def]
    for error in sorted(
        validator.iter_errors(block), key=lambda e: list(e.absolute_path)
    ):
        err_path = list(error.absolute_path)
        # Top-level unknown keys are handled above. cfnlint's validator reports the
        # offending key in the path (length 1), so skip those and keep nested
        # (length >= 2) additionalProperties violations are genuine shape problems.
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


# ---------------------------------------------------------------------------
# Rule base behavior (mixin -- shared config and targeting logic extracted
# per the DRY principle; NOT a CloudFormationLintRule subclass so cfn-lint's
# plugin loader does not register it as a standalone rule)
# ---------------------------------------------------------------------------


class _ContextRuleMixin:
    """Shared config (severity, extra incidental patterns) and iteration helpers."""

    config: dict[str, Any]
    id: str

    def __init__(self) -> None:
        super().__init__()
        # CloudFormationLintRule.__init__ resets config_definition to {} on the
        # instance, so the shared definition must be (re)applied here. cfn-lint's
        # rule registration then calls configure(), which applies these defaults
        # plus any user-provided --configure-rule overrides.
        self.config_definition = {
            "severity": dict(_SEVERITY_CONFIG),
            "additional_incidental_patterns": dict(_PATTERNS_CONFIG),
            "additional_low_value_types": dict(_PATTERNS_CONFIG),
        }
        self.config.setdefault("severity", _DEFAULT_SEVERITY)
        self.config.setdefault("additional_incidental_patterns", [])
        self.config.setdefault("additional_low_value_types", [])

    @property
    def severity(self) -> str:
        configured = (
            self.config.get("severity") if isinstance(self.config, dict) else None
        )
        if configured in _VALID_SEVERITIES:
            return str(configured)
        return _DEFAULT_SEVERITY

    def _extra_patterns(self) -> list[str]:
        patterns = self.config.get("additional_incidental_patterns", [])
        return [str(p) for p in patterns] if isinstance(patterns, list) else []

    def _extra_low_value_types(self) -> list[str]:
        types = self.config.get("additional_low_value_types", [])
        return [str(t) for t in types] if isinstance(types, list) else []

    def _significant_resources(self, cfn: Any) -> list[tuple[str, dict[str, Any]]]:
        """Primary resources *required* to carry context.

        Non-incidental resources minus subordinate/low-value types. Used by
        missing-context (W4010); the validate-supplied rules use
        ``_primary_resources`` so they still check any context present on a
        low-value resource.
        """
        low_value_extra = self._extra_low_value_types()
        return [
            (logical_id, resource)
            for logical_id, resource in self._primary_resources(cfn)
            if not _is_low_value(resource, low_value_extra)
        ]

    def _primary_resources(self, cfn: Any) -> list[tuple[str, dict[str, Any]]]:
        """Return (logical_id, resource) pairs for non-incidental resources."""
        extra = self._extra_patterns()
        results = []
        for logical_id, resource in cfn.get_resources().items():
            if not isinstance(resource, dict):
                continue
            if _is_incidental(str(logical_id), resource, extra):
                continue
            results.append((str(logical_id), resource))
        return results

    def _schema_matches(self, cfn: Any) -> list[RuleMatch]:
        """RuleMatches for every schema violation across all Context blocks."""
        matches = []
        for logical_id, resource in self._primary_resources(cfn):
            context = _get_context(resource)
            if context is None or _is_opted_out(context):
                continue
            base_path = ["Resources", logical_id, "Metadata", CONTEXT_KEY]
            for finding in _schema_findings(
                context, "ResourceContext", base_path, logical_id
            ):
                matches.append(RuleMatch(finding.path, finding.message))
        template_metadata = cfn.template.get("Metadata")
        if isinstance(template_metadata, dict) and CONTEXT_KEY in template_metadata:
            context = template_metadata[CONTEXT_KEY]
            if not _is_opted_out(context):
                for finding in _schema_findings(
                    context, "TemplateContext", ["Metadata", CONTEXT_KEY], "Template"
                ):
                    matches.append(RuleMatch(finding.path, finding.message))
        return matches


# ---------------------------------------------------------------------------
# Core rules
# ---------------------------------------------------------------------------


class ContextMissing(_ContextRuleMixin, CloudFormationLintRule):
    """missing-context: a primary resource has no Context metadata block at all."""

    id = "W4010"
    shortdesc = "Template or significant resource has no Context block"
    description = (
        f"Flags a template whose top-level Metadata has no {_CONTEXT_DISPLAY}"
        f" block, and significant resources missing a {_CONTEXT_DISPLAY}"
        " block. Incidental/framework resources and subordinate low-value"
        " types (e.g. AWS::Logs::LogGroup) are not required to carry context."
        " Rationale written as YAML comments is not visible to cfn-lint;"
        " suppress this rule on templates that document context that way."
        " Disabled by default; set require_context=true to require Context"
        " metadata."
    )
    source_url = "https://github.com/aws/aws-cdk/pull/38381"
    tags = ["metadata", "context"]

    def __init__(self) -> None:
        super().__init__()
        # missing-context is a team policy opt-in: requiring a Context block is a
        # convention a repo adopts, not a universal lint. Off by default so it does
        # not fire on templates that have not adopted the convention; enable with
        # --configure-rule W4010:require_context=true (or a .cfnlintrc). The
        # validate-supplied rules (W4011/W4012) need no such gate -- they only fire
        # when an author has already written a Context block.
        self.config_definition["require_context"] = {
            "default": False,
            "type": "boolean",
        }
        self.config.setdefault("require_context", False)

    def match(self, cfn: Any) -> list[RuleMatch]:
        if not self.config.get("require_context", False):
            return []
        matches = []
        significant = self._significant_resources(cfn)
        # Finding 1 -- template diagnostic: an architecture summary describes how
        # multiple components relate, so require it only when the template has more
        # than one significant resource. A single significant resource's own 'why'
        # already captures its rationale.
        template_metadata = cfn.template.get("Metadata")
        has_template_context = (
            isinstance(template_metadata, dict) and CONTEXT_KEY in template_metadata
        )
        if len(significant) >= 2 and not has_template_context:
            matches.append(RuleMatch(["Metadata"], _MSG_TEMPLATE_MISSING))
        # Finding 2 -- resource aggregate: a single finding for every significant
        # resource missing context. The first resource is the primary match; each
        # remaining resource rides in the primary's ``.context`` list. cfn-lint emits
        # the primary plus one linked child per related resource (shared parent id),
        # each retaining its own source location -- reproducing the standard's
        # "primary + relatedResources" shape rather than one finding per resource.
        missing = [
            (logical_id, resource)
            for logical_id, resource in significant
            if _get_context(resource) is None
        ]
        if missing:
            matches.append(self._resource_aggregate(cfn, missing))
        return matches

    def _resource_aggregate(
        self, cfn: Any, missing: list[tuple[str, dict[str, Any]]]
    ) -> RuleMatch:
        """Build one aggregate missing-context finding covering ``missing`` resources.

        The first resource is the primary; the rest become child ``RuleMatch`` objects
        on ``.context``. cfn-lint links each child to the primary via ``parent_id`` and
        preserves each resource's own location (set explicitly here, since cfn-lint
        prepends the primary's path to a child's path when resolving location).
        """
        summary = ", ".join(
            f"{logical_id} ({resource.get('Type', 'unknown type')})"
            for logical_id, resource in missing
        )
        primary_id, _ = missing[0]
        primary = RuleMatch(
            ["Resources", primary_id],
            _MSG_RESOURCE_AGGREGATE.format(
                context_display=_CONTEXT_DISPLAY, summary=summary
            ),
        )
        related: list[RuleMatch] = []
        for logical_id, _ in missing[1:]:
            location = cfn.get_location_yaml(cfn.template, ["Resources", logical_id])
            # RuleMatch stores extra kwargs as attributes; 'location' is
            # consumed by the match resolver to keep each child's own span.
            # Path is relative (just the logical ID) since the framework prepends
            # the parent's path when resolving child matches.
            extra = {"location": location} if location else {}
            child = RuleMatch(
                [logical_id],
                _MSG_CHILD_MISSING,
                **extra,
            )
            related.append(child)
        primary.context = related
        return primary


class ContextMissingWhy(_ContextRuleMixin, CloudFormationLintRule):
    """missing-why: Context exists but has neither 'why' nor a 'gaps' entry."""

    id = "W4011"
    shortdesc = "Context metadata block has no 'why'"
    description = (
        "Flags Context blocks lacking a 'why' rationale and any 'gaps' entry"
        " acknowledging the unknown."
    )
    source_url = ContextMissing.source_url
    tags = ["metadata", "context"]

    def match(self, cfn: Any) -> list[RuleMatch]:
        matches = []
        for logical_id, resource in self._primary_resources(cfn):
            context = _get_context(resource)
            if not isinstance(context, dict) or _is_opted_out(context):
                continue
            why = context.get("why")
            gaps = context.get("gaps")
            has_why = isinstance(why, str) and why.strip()
            has_gaps = isinstance(gaps, list) and len(gaps) > 0
            if has_why or has_gaps:
                continue
            matches.append(
                RuleMatch(
                    ["Resources", logical_id, "Metadata", CONTEXT_KEY],
                    _MSG_MISSING_WHY.format(
                        logical_id=logical_id, context_display=_CONTEXT_DISPLAY
                    ),
                )
            )
        return matches


class ContextSchemaViolation(_ContextRuleMixin, CloudFormationLintRule):
    """schema-violation: a supplied Context block fails schema v1 validation."""

    id = "W4012"
    shortdesc = "Context field does not match the schema"
    description = (
        "Flags a supplied Context block that does not match the Context schema v1: "
        "fields with the wrong type or shape (e.g. 'must' a string not an array; "
        "'trust' missing required 'src'/'conf'), enum fields with an unrecognized "
        "value (mutable/mutability levels, trust.src, trust.conf), and fields placed "
        "at the wrong level (template-only fields on a resource, or resource-only "
        "fields on the template)."
    )
    source_url = ContextMissing.source_url
    tags = ["metadata", "context"]

    def match(self, cfn: Any) -> list[RuleMatch]:
        return self._schema_matches(cfn)
