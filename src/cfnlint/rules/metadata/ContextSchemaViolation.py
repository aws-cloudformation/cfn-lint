"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.rules.metadata._BaseContext import _CONTEXT_DISPLAY, ContextRuleMixin


class ContextSchemaViolation(ContextRuleMixin, CloudFormationLintRule):
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
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-attribute-metadata.html#aws-attribute-metadata-context-schema"
    tags = ["metadata", "context"]

    def match(self, cfn: Any) -> list[RuleMatch]:
        if self._is_cdk_template(cfn):
            return []
        return self._schema_matches(cfn)
