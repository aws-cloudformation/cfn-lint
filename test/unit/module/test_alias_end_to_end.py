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

    def test_scalar_alias_warns(self):
        template = (
            'AWSTemplateFormatVersion: "2010-09-09"\n'
            "Resources:\n"
            "  FirstLogGroup:\n"
            "    Type: AWS::Logs::LogGroup\n"
            "    Properties:\n"
            "      RetentionInDays: &Retention 30\n"
            "  SecondLogGroup:\n"
            "    Type: AWS::Logs::LogGroup\n"
            "    Properties:\n"
            "      RetentionInDays: *Retention\n"
        )
        matches = lint_all(template)
        aliases = [m for m in matches if m.rule.id == "W1101"]
        # Reported at the alias, not the anchor
        self.assertEqual(
            [(m.linenumber, m.columnnumber) for m in aliases],
            [(10, 24)],
            f"Got {matches!r}",
        )

    def test_alias_warns_after_language_extensions_transform(self):
        # The transform replaces the template, so the aliases recorded by the
        # decoder must survive it
        template = (
            "Transform: AWS::LanguageExtensions\n"
            "Resources:\n"
            "  Fn::ForEach::Topics:\n"
            "    - Name\n"
            "    - [A, B]\n"
            "    - Topic${Name}:\n"
            "        Type: AWS::SNS::Topic\n"
            "        Properties:\n"
            "          DisplayName: &name shared\n"
            "  Queue:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Properties:\n"
            "      QueueName: *name\n"
        )
        matches = lint_all(template)
        aliases = [m for m in matches if m.rule.id == "W1101"]
        self.assertEqual(
            [(m.linenumber, m.columnnumber) for m in aliases],
            [(13, 18)],
            f"Got {matches!r}",
        )

    def test_alias_in_sam_template_does_not_warn(self):
        template = (
            "Transform: AWS::Serverless-2016-10-31\n"
            "Resources:\n"
            "  Topic1:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Properties:\n"
            "      DisplayName: &name shared\n"
            "  Topic2:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Properties:\n"
            "      DisplayName: *name\n"
        )
        matches = lint_all(template)
        rule_ids = [m.rule.id for m in matches]
        self.assertNotIn("W1101", rule_ids, f"Got {matches!r}")
