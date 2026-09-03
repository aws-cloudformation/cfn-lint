"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from unittest import TestCase

from cfnlint import lint_all


def _nested_alias_template(levels: int, fan: int = 2) -> str:
    lines = [
        "Resources:",
        "  Data:",
        "    Type: AWS::CloudFormation::WaitConditionHandle",
        "    Metadata:",
        '      l0: &l0 ["x", "x"]',
    ]
    for n in range(1, levels + 1):
        refs = ", ".join([f"*l{n - 1}"] * fan)
        lines.append(f"      l{n}: &l{n} [{refs}]")
    lines.append(f"      big: *l{levels}")
    return "\n".join(lines) + "\n"


class TestAliasEndToEnd(TestCase):
    """End-to-end (decode -> runner -> rules) coverage for YAML aliases."""

    def test_alias_amplification_fails_fast(self):
        matches = lint_all(_nested_alias_template(levels=19))
        rule_ids = [m.rule.id for m in matches]
        # The load-time guard short-circuits with a single parse error and the
        # template is never linted (no rule findings, no hang).
        self.assertEqual(rule_ids, ["E0000"], f"Got {matches!r}")
        self.assertIn("YAML aliases", matches[0].message)

    def test_reasonable_alias_warns_but_still_lints(self):
        template = (
            "Resources:\n"
            "  Topic1:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Properties:\n"
            "      Tags: &shared\n"
            "        - Key: env\n"
            "          Value: test\n"
            "  Topic2:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Properties:\n"
            "      Tags: *shared\n"
        )
        matches = lint_all(template)
        rule_ids = [m.rule.id for m in matches]
        # The alias is warned about (W1101) and the template is still linted
        # (no fatal parse error).
        self.assertIn("W1101", rule_ids, f"Got {matches!r}")
        self.assertNotIn("E0000", rule_ids, f"Got {matches!r}")
