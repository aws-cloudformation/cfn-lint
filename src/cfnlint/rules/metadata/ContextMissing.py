"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.rules.metadata._BaseContext import (
    _CONTEXT_DISPLAY,
    _PATTERNS_CONFIG,
    CONTEXT_KEY,
    CONTEXT_SCHEMA_URL,
    ContextRuleMixin,
    _get_context,
)

# Types not required to carry context (subordinate/policy resources).
# Supplied context is still validated by W4012. Extend via
# additional_low_value_types.
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


def _is_low_value(resource: dict[str, Any], extra_types: list[str]) -> bool:
    """True for subordinate/low-value types, exempt from missing-context here.

    Any context these do supply is still validated by W4012.
    """
    rtype = resource.get("Type")
    if not isinstance(rtype, str):
        return False
    return rtype in _LOW_VALUE_TYPES or rtype in extra_types


def _is_module(resource: dict[str, Any]) -> bool:
    """True for a MODULE pseudo-resource ('*::MODULE').

    A module's Type can't say if it's architecture-relevant, so only the
    missing-context requirement is suppressed; supplied context is still
    validated by W4012.
    """
    rtype = resource.get("Type")
    return isinstance(rtype, str) and rtype.endswith("::MODULE")


class ContextMissing(ContextRuleMixin, CloudFormationLintRule):
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
    source_url = CONTEXT_SCHEMA_URL
    tags = ["metadata", "context"]

    def __init__(self) -> None:
        super().__init__()
        # I4010 is the only rule that exempts low-value types from the
        # missing-context requirement. W4011/W4012 validate supplied context
        # everywhere, so they don't expose this option.
        self.config_definition["additional_low_value_types"] = dict(_PATTERNS_CONFIG)
        self.config.setdefault("additional_low_value_types", [])

    def match(self, cfn: Any) -> list[RuleMatch]:
        if self._is_cdk_template(cfn):
            return []
        matches = []
        significant = self._significant_resources(cfn)
        # Apply per-resource ignore_checks here: runner's post-hoc filter keys
        # off match path, which would suppress the whole aggregate or miss the
        # template finding. Exact-match keys only (not prefixes).
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

    def _significant_resources(self, cfn: Any) -> list[tuple[str, dict[str, Any]]]:
        """Primary resources *required* to carry context.

        Non-incidental resources minus subordinate/low-value types and MODULE
        pseudo-resources. W4011/W4012 use ``_primary_resources`` directly so they
        still check any context present on a low-value resource or a module.
        """
        low_value_extra = self._extra_low_value_types()
        return [
            (logical_id, resource)
            for logical_id, resource in self._primary_resources(cfn)
            if not _is_low_value(resource, low_value_extra) and not _is_module(resource)
        ]

    def _extra_low_value_types(self) -> list[str]:
        types = self.config.get("additional_low_value_types", [])
        return [str(t) for t in types] if isinstance(types, list) else []

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
