"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.rules.metadata._BaseContext import (
    _CONTEXT_DISPLAY,
    CONTEXT_KEY,
    CONTEXT_SCHEMA_URL,
    ContextRuleMixin,
    _get_context,
)

_MSG_MISSING_WHY = (
    "{logical_id}: {context_display} has no 'why'. Add 'why': purpose + notable "
    'choices, telegraphic style (e.g. "buffer order events async; FIFO rejected '
    '(throughput > ordering)") -- or set trust to {{src: infer, conf: low, '
    'note: "rationale not documented"}}. Never restate the Type/logical '
    "id/property values."
)


class ContextMissingWhy(ContextRuleMixin, CloudFormationLintRule):
    """missing-why: Context exists but has no 'why' and no conf: low trust block."""

    id = "W4011"
    experimental = True
    shortdesc = "Context block has no 'why'"
    description = (
        f"Check that a {_CONTEXT_DISPLAY} block records a"
        " 'why' rationale, or declares a trust block with conf: low"
        " acknowledging the rationale is undocumented."
    )
    source_url = CONTEXT_SCHEMA_URL
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
            # Only low confidence excuses a missing 'why'. medium/high assert
            # the rationale is at least partly known, so they do not.
            has_trust = isinstance(trust, dict) and trust.get("conf") == "low"
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
