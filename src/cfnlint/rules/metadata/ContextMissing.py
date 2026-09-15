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
    MSG_RESOURCE_AGGREGATE,
    MSG_TEMPLATE_MISSING,
    ContextRuleMixin,
    _get_context,
)


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
            matches.append(RuleMatch(["Metadata"], MSG_TEMPLATE_MISSING))
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
            MSG_RESOURCE_AGGREGATE.format(
                context_display=_CONTEXT_DISPLAY, summary=summary
            ),
        )
