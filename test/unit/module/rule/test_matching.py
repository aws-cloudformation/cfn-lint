"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from typing import Any

from cfnlint.rules import CloudFormationLintRule, Match, RuleMatch
from cfnlint.rules._rule import matching


class rule(CloudFormationLintRule):
    id: str = "ETest"
    pass


rule_match = RuleMatch([], "Message", rule=rule(), location=(0, 0, 0, 0))


class TestMatching(BaseTestCase):
    """Test Matching Wrapper"""

    def example(self: Any, *args: Any, **kwargs: Any):
        return [rule_match]

    def test_matching_location(self):
        f = matching("example")
        r = f(self.example)
        t = r(self, "", None)
        self.assertEqual(
            list(t),
            [
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename="",
                    rule=rule(),
                    message="Message",
                    rulematch_obj=rule_match,
                )
            ],
        )

    def test_compare(self):
        rule_match_1 = RuleMatch(
            ["path"], "Message", rule=rule(), location=(0, 0, 0, 0)
        )
        rule_match_2 = RuleMatch(
            ["path"], "Message", rule=rule(), location=(0, 0, 0, 0)
        )
        self.assertEqual(rule_match_1, rule_match_2)

        rule_match_3 = RuleMatch(
            ["path"], "New Message", rule=rule(), location=(1, 1, 1, 1)
        )
        self.assertNotEqual(rule_match_1, rule_match_3)
