"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from typing import Any

from cfnlint.rules import CloudFormationLintRule, Match, RuleMatch, matching


class rule(CloudFormationLintRule):
    id: str = "ETest"
    pass


rule_match = RuleMatch([], "Message", rule=rule(), location=(0, 0, 0, 0))


class TestMatching(BaseTestCase):
    """Test Matching Wrapper"""

    def setUp(self) -> None:
        return super().setUp()

    def example(self: Any, *args: Any, **kwargs: Any):
        return [rule_match]

    def test_matching_location(self):
        f = matching("example")
        r = f(self.example)
        t = r(self, "", None)
        self.assertEqual(t, [Match(1, 1, 1, 1, "", rule(), "Message", rule_match)])
