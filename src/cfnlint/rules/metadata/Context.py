"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

# cfn-lint rules for CloudFormation Metadata.com.aws.cloudformation.Context
# blocks, a convention for carrying design rationale in template metadata: a
# top-level architecture summary plus per-resource "why / must / mutability"
# notes (aws/aws-cdk#38381).
#
#   I4010 missing-context    Template or significant resource has no Context block
#   I4011 missing-why        Context present but has neither 'why' nor 'trust'
#   I4012 schema-violation   Supplied Context field fails schema validation
#
# All three are experimental and informational, so both --include-experimental
# and --include-checks I are required before any of them emits a finding.
#
# CDK-synthesized templates are skipped entirely (detected by AWS::CDK::Metadata
# or aws:cdk:path on any resource). The user authored L2/L3 constructs, not raw
# CloudFormation, so context validation does not apply.

from __future__ import annotations

import re
from typing import Any

import cfnlint.data.schemas.other.metadata
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import StandardValidator
from cfnlint.rules import CloudFormationLintRule, RuleMatch

CONTEXT_KEY = "com.aws.cloudformation.Context"
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


_VALIDATORS: dict[str, StandardValidator] = {
    "ResourceContext": StandardValidator(_get_subschema("ResourceContext")),
    "TemplateContext": StandardValidator(_get_subschema("TemplateContext")),
}

# Incidental resources: CDK helpers no author chose. CDK sees structure; cfn-lint
# sees only names, so it approximates via patterns. Extend with config option
# additional_incidental_patterns. The AwsCustomResource singleton ID is fixed
# (changing it orphans deployed functions).
_CDK_AWS_CUSTOM_RESOURCE_SINGLETON_ID = "AWS679f53fac002430cb0da5b7982bd2287"

_INCIDENTAL_PATH_PATTERN = re.compile(
    r"LogRetention|(?:^|/)Provider(?:/|$)|framework-onEvent|framework-isComplete"
    rf"|framework-onTimeout|{_CDK_AWS_CUSTOM_RESOURCE_SINGLETON_ID}"
)
# CFN strips hyphens at synth (framework-onEvent -> frameworkonEvent).
_INCIDENTAL_ID_PATTERN = re.compile(
    r"^LogRetention|(?<=[a-z])Provider(?=framework)"
    r"|frameworkonEvent|frameworkisComplete"
    rf"|frameworkonTimeout|^{_CDK_AWS_CUSTOM_RESOURCE_SINGLETON_ID}$"
)
_CDK_METADATA_TYPE = "AWS::CDK::Metadata"
_CDK_METADATA_LOGICAL_ID = "CDKMetadata"
_CDK_PATH_KEY = "aws:cdk:path"

# Types not required to carry context (subordinate/policy resources).
# Supplied context is still validated. Extend via additional_low_value_types.
_LOW_VALUE_TYPES = frozenset(
    {
        "AWS::IAM::Policy",
        "AWS::Lambda::Permission",
        "AWS::Logs::LogGroup",
        "AWS::Logs::LogStream",
        "AWS::S3::BucketPolicy",
        "AWS::SNS::TopicPolicy",
        "AWS::SQS::QueuePolicy",
    }
)

_PATTERNS_CONFIG: dict[str, Any] = {"default": [], "type": "list", "itemtype": "string"}


# Shared helpers, module-level so the mixin below stays stateless.


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
    if _INCIDENTAL_ID_PATTERN.search(logical_id):
        return True
    if cdk_path and _INCIDENTAL_PATH_PATTERN.search(str(cdk_path)):
        return True
    # User-configured patterns apply to both the logical ID and the cdk path.
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
    suppressed by I4010), but any context they supply is still validated.
    """
    rtype = resource.get("Type")
    if not isinstance(rtype, str):
        return False
    return rtype in _LOW_VALUE_TYPES or rtype in extra_types


def _is_module(resource: dict[str, Any]) -> bool:
    """True for a MODULE pseudo-resource (a '*::MODULE' type).

    A module's Type says nothing about whether it is architecture-relevant --
    it could wrap one log bucket or a whole data tier -- so only the
    missing-context requirement is suppressed. Supplied context is still
    validated.
    """
    rtype = resource.get("Type")
    return isinstance(rtype, str) and rtype.endswith("::MODULE")


def _get_context(resource: dict[str, Any]) -> Any:
    """Return the resource's Context metadata block (any shape), or None."""
    metadata = resource.get("Metadata")
    if not isinstance(metadata, dict):
        return None
    return metadata.get(CONTEXT_KEY)


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
_MSG_RESOURCE_AGGREGATE = (
    "These architecture-relevant resources are missing {context_display}: "
    "{summary}. For each listed resource, add {context_display}. Set 'why' to the "
    "resource's purpose or design rationale. If the rationale is not documented, "
    'set trust to {{src: infer, conf: low, note: "rationale not documented"}} '
    "instead of guessing. Add 'must' as a list only for known constraints whose "
    "violation would break the system; otherwise omit it. Leave unlisted "
    "resources unchanged."
)
_MSG_MISSING_WHY = (
    "{logical_id}: {context_display} has no 'why'. Add 'why': purpose + notable "
    'choices, telegraphic style (e.g. "buffer order events async; FIFO rejected '
    '(throughput > ordering)") -- or set trust to {{src: infer, conf: low, '
    'note: "rationale not documented"}}. Never restate the Type/logical '
    "id/property values."
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


class _ContextRuleMixin:
    """Shared config (extra incidental patterns) and iteration helpers."""

    config: dict[str, Any]
    id: str

    def __init__(self) -> None:
        super().__init__()
        # CloudFormationLintRule.__init__ resets config_definition to {} on the
        # instance, so the shared definition must be (re)applied here. cfn-lint's
        # rule registration then calls configure(), which applies these defaults
        # plus any user-provided --configure-rule overrides.
        #
        # Only additional_incidental_patterns is shared (all three rules use
        # _primary_resources). additional_low_value_types is I4010-only because
        # I4011/I4012 validate supplied context everywhere -- low-value resources
        # are not exempt from validation.
        self.config_definition = {
            "additional_incidental_patterns": dict(_PATTERNS_CONFIG),
        }
        self.config.setdefault("additional_incidental_patterns", [])

    @staticmethod
    def _is_cdk_template(cfn: Any) -> bool:
        """True when the template was synthesized by CDK.

        CDK-synthesized templates are out of scope for context validation
        because the user authored L2/L3 constructs, not raw CloudFormation.
        Detection: the ``AWS::CDK::Metadata`` resource, the ``CDKMetadata``
        logical ID, or any resource carrying ``aws:cdk:path`` metadata (covers
        templates synthesized with analyticsReporting disabled).
        """
        for logical_id, resource in cfn.get_resources().items():
            if (
                resource.get("Type") == _CDK_METADATA_TYPE
                or str(logical_id) == _CDK_METADATA_LOGICAL_ID
            ):
                return True
            metadata = resource.get("Metadata")
            if isinstance(metadata, dict) and _CDK_PATH_KEY in metadata:
                return True
        return False

    def _extra_patterns(self) -> list[str]:
        patterns = self.config.get("additional_incidental_patterns", [])
        return [str(p) for p in patterns] if isinstance(patterns, list) else []

    def _extra_low_value_types(self) -> list[str]:
        types = self.config.get("additional_low_value_types", [])
        return [str(t) for t in types] if isinstance(types, list) else []

    def _significant_resources(self, cfn: Any) -> list[tuple[str, dict[str, Any]]]:
        """Primary resources *required* to carry context.

        Non-incidental resources minus subordinate/low-value types and MODULE
        pseudo-resources. Used by missing-context (I4010); the validate-supplied
        rules use ``_primary_resources`` so they still check any context present
        on a low-value resource or a module.
        """
        low_value_extra = self._extra_low_value_types()
        return [
            (logical_id, resource)
            for logical_id, resource in self._primary_resources(cfn)
            if not _is_low_value(resource, low_value_extra) and not _is_module(resource)
        ]

    def _primary_resources(self, cfn: Any) -> list[tuple[str, dict[str, Any]]]:
        """Return (logical_id, resource) pairs for non-incidental resources."""
        extra = self._extra_patterns()
        results = []
        for logical_id, resource in cfn.get_resources().items():
            if _is_incidental(str(logical_id), resource, extra):
                continue
            results.append((str(logical_id), resource))
        return results

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


class ContextMissing(_ContextRuleMixin, CloudFormationLintRule):
    """missing-context: an architecture-relevant resource has no Context block."""

    id = "I4010"
    experimental = True
    shortdesc = "Template or architecture-relevant resource has no Context block"
    description = (
        f"Check for a machine-readable {_CONTEXT_DISPLAY}"
        " block on the template and on architecture-relevant resources."
        " Incidental framework resources, subordinate types such as"
        " AWS::Logs::LogGroup, and resource policies (AWS::IAM::Policy,"
        " BucketPolicy, TopicPolicy, QueuePolicy, Lambda::Permission)"
        " are not expected to carry one."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-attribute-metadata.html#aws-attribute-metadata-context-schema"
    tags = ["metadata", "context"]

    def __init__(self) -> None:
        super().__init__()
        # I4010 is the only rule that exempts low-value types from the
        # missing-context requirement. I4011/I4012 validate supplied context
        # everywhere, so they don't expose this option.
        self.config_definition["additional_low_value_types"] = dict(_PATTERNS_CONFIG)
        self.config.setdefault("additional_low_value_types", [])

    def match(self, cfn: Any) -> list[RuleMatch]:
        if self._is_cdk_template(cfn):
            return []
        matches = []
        significant = self._significant_resources(cfn)
        # Both findings aggregate over many resources, so per-resource
        # ignore_checks has to be applied here rather than left to the runner's
        # post-hoc match filter: that filter keys off a match's own path, which
        # would suppress the whole aggregate because one listed resource happens
        # to be first, and never suppresses the template finding at all (its
        # path does not start with "Resources"). Filtering the input instead
        # means suppressing one resource drops just that resource from both
        # findings, and suppressing all of them drops both findings.
        #
        # Keys are matched exactly, as the runner does -- a directive key is a
        # literal rule id, not a prefix.
        directives = cfn.get_directives()
        suppressed = set(directives.get(self.id, []))
        missing = [
            (logical_id, resource)
            for logical_id, resource in significant
            if _get_context(resource) is None and logical_id not in suppressed
        ]
        # An architecture summary describes how components relate, so require one
        # only above a single resource -- one resource's own 'why' covers it.
        template_metadata = cfn.template.get("Metadata")
        has_template_context = (
            isinstance(template_metadata, dict) and CONTEXT_KEY in template_metadata
        )
        if len(missing) >= 2 and not has_template_context:
            matches.append(RuleMatch(["Metadata"], _MSG_TEMPLATE_MISSING))
        if missing:
            matches.append(self._resource_aggregate(missing))
        return matches

    def _resource_aggregate(
        self, missing: list[tuple[str, dict[str, Any]]]
    ) -> RuleMatch:
        """Build one aggregate finding covering ``missing`` resources."""
        summary = ", ".join(
            f"{logical_id} ({resource.get('Type', 'unknown type')})"
            for logical_id, resource in missing
        )
        primary_id, _ = missing[0]
        return RuleMatch(
            ["Resources", primary_id],
            _MSG_RESOURCE_AGGREGATE.format(
                context_display=_CONTEXT_DISPLAY, summary=summary
            ),
        )


class ContextMissingWhy(_ContextRuleMixin, CloudFormationLintRule):
    """missing-why: Context exists but has no 'why' and no reduced-confidence trust."""

    id = "I4011"
    experimental = True
    shortdesc = "Context block has no 'why'"
    description = (
        f"Check that a {_CONTEXT_DISPLAY} block records a"
        " 'why' rationale, or declares a trust block with reduced confidence"
        " acknowledging the rationale is undocumented."
    )
    source_url = ContextMissing.source_url
    tags = ["metadata", "context"]

    def match(self, cfn: Any) -> list[RuleMatch]:
        if self._is_cdk_template(cfn):
            return []
        matches = []
        for logical_id, resource in self._primary_resources(cfn):
            context = _get_context(resource)
            if not isinstance(context, dict):
                continue
            why = context.get("why")
            trust = context.get("trust")
            has_why = isinstance(why, str) and bool(why.strip())
            # Only reduced confidence excuses a missing 'why'. conf: high is a
            # claim that the rationale IS known, so it does not.
            has_trust = isinstance(trust, dict) and trust.get("conf") in (
                "low",
                "medium",
            )
            if has_why or has_trust:
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

    id = "I4012"
    experimental = True
    shortdesc = "Context field does not match the schema"
    description = (
        f"Check a supplied {_CONTEXT_DISPLAY} block against"
        " the Context schema: field types and shapes, recognized enum values,"
        " and fields placed at the correct level (template fields on the"
        " template, resource fields on resources)."
    )
    source_url = ContextMissing.source_url
    tags = ["metadata", "context"]

    def match(self, cfn: Any) -> list[RuleMatch]:
        if self._is_cdk_template(cfn):
            return []
        return self._schema_matches(cfn)
