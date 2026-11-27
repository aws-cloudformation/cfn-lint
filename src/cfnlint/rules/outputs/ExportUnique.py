"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class ExportUnique(CloudFormationLintRule):
    """Check that output export names are unique within a template"""

    id = "E6103"
    shortdesc = "Validate that output export names are unique"
    description = (
        "Make sure no two outputs in the same template export the "
        "same name, which CloudFormation rejects at CreateStack"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def _conditions_can_both_be_true(
        self, cfn: Template, condition1: Any, condition2: Any
    ) -> bool:
        """Whether two outputs can exist at the same time.

        An output without a Condition always exists. Two outputs
        with conditions collide only when there is a scenario in
        which both conditions are true.
        """
        if not isinstance(condition1, str) or not isinstance(condition2, str):
            return True
        if condition1 == condition2:
            return True
        scenarios = cfn.conditions.build_scenarios(
            {condition1: {True}, condition2: {True}}
        )
        return any(True for _ in scenarios)

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []
        outputs = cfn.template.get("Outputs")
        if not isinstance(outputs, dict):
            return matches

        # export name -> list of (output name, condition)
        exports: dict[str, list[tuple[str, Any]]] = {}
        for output_name, output in outputs.items():
            if not isinstance(output, dict):
                continue
            export = output.get("Export")
            if not isinstance(export, dict):
                continue
            name = export.get("Name")
            # Only literal names can be compared. Names built with
            # intrinsic functions (Fn::Sub, Fn::Join, Fn::If, ...)
            # are out of scope for this check.
            if not isinstance(name, str):
                continue
            exports.setdefault(name, []).append(
                (output_name, output.get("Condition"))
            )

        for name, entries in exports.items():
            if len(entries) < 2:
                continue
            for output_name, condition in entries:
                duplicates = [
                    other
                    for other, other_condition in entries
                    if other != output_name
                    and self._conditions_can_both_be_true(
                        cfn, condition, other_condition
                    )
                ]
                if not duplicates:
                    continue
                path = ["Outputs", output_name, "Export", "Name"]
                message = (
                    f"Export name {name!r} is also used by output(s) "
                    f"{sorted(duplicates)!r}. Export names must be "
                    "unique within a template"
                )
                matches.append(RuleMatch(path, message))

        return matches
