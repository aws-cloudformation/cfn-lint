"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.decode import decode_str


def _nested_alias_template(levels: int, fan: int = 2) -> str:
    """Build a "billion laughs" template.

    Each anchor references the previous one ``fan`` times, so ``l{levels}``
    expands to ``2 * fan ** levels`` leaves while the source stays tiny.
    """
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


class TestAliasExpansion(BaseTestCase):
    def test_alias_amplification_is_rejected(self):
        # 2 ** 19 == 524288 leaves, well over the 250k node budget
        template = _nested_alias_template(levels=19)

        result, matches = decode_str(template)

        self.assertIsNone(result)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")
        self.assertIn("YAML aliases", matches[0].message)

    def test_reasonable_alias_use_is_allowed(self):
        # A handful of aliases stays well under the budget and loads fine
        template = _nested_alias_template(levels=4)

        result, matches = decode_str(template)

        self.assertListEqual(matches, [])
        self.assertIsNotNone(result)
        self.assertIn("Resources", result)

    def test_template_without_aliases_is_unaffected(self):
        template = "Resources:\n  Topic:\n    Type: AWS::SNS::Topic\n"

        result, matches = decode_str(template)

        self.assertListEqual(matches, [])
        self.assertIsNotNone(result)

    def test_guard_function_directly(self):
        from cfnlint.decode.cfn_yaml import (
            _MAX_EXPANDED_NODES,
            CfnParseError,
            _guard_alias_expansion,
        )

        # Under the budget: passes silently
        _guard_alias_expansion({"A": [1, 2, 3]}, "test")

        # Over the budget: raises CfnParseError with an E0000 match
        shared = list(range(10))
        over_budget = {str(i): shared for i in range(_MAX_EXPANDED_NODES)}
        with self.assertRaises(CfnParseError) as err:
            _guard_alias_expansion(over_budget, "test")
        self.assertEqual(err.exception.matches[0].rule.id, "E0000")
