"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint import ConfigMixIn
from cfnlint.rules import CloudFormationLintRule, Match
from cfnlint.runner import Runner


class ErrorRule(CloudFormationLintRule):
    id = "E0000"
    description = "Error"


class WarningRule(CloudFormationLintRule):
    id = "W0000"
    description = "Warning"


class InformationRule(CloudFormationLintRule):
    id = "I0000"
    description = "Informational"


error_match = Match("", ErrorRule(), "", 0, 0, 0, 0)
warning_match = Match("", WarningRule(), "", 0, 0, 0, 0)
informational_match = Match("", InformationRule(), "", 0, 0, 0, 0)


class TestExitCodes(BaseTestCase):
    """Test Exit Codes"""

    def test_exit_code_zero(self):
        params = [
            [[], "informational", 0],
            [[error_match], "informational", 2],
            [[error_match], "warning", 2],
            [[error_match], "error", 2],
            [[error_match], "none", 0],
            [[error_match, warning_match], "informational", 6],
            [[error_match, warning_match], "warning", 6],
            [[error_match, warning_match], "error", 2],
            [[error_match, warning_match], "none", 0],
            [[warning_match, informational_match], "informational", 12],
            [[warning_match, informational_match], "warning", 4],
            [[warning_match, informational_match], "error", 0],
            [[warning_match, informational_match], "none", 0],
            [[error_match, informational_match], "informational", 10],
            [[error_match, informational_match], "warning", 2],
            [[error_match, informational_match], "error", 2],
            [[error_match, informational_match], "none", 0],
            [[error_match, warning_match, informational_match], "informational", 14],
            [[error_match, warning_match, informational_match], "warning", 6],
            [[error_match, warning_match, informational_match], "error", 2],
            [[error_match, warning_match, informational_match], "none", 0],
        ]

        for matches, level, exit_code in params:
            with self.subTest():
                runner = Runner(ConfigMixIn(non_zero_exit_code=level))
                match_names = [x.rule.description for x in matches]
                with self.assertRaises(SystemExit) as e:
                    runner._exit(matches)
                self.assertEqual(
                    e.exception.code,
                    exit_code,
                    (
                        f"{match_names!r} matches with {level!r} "
                        f"level should yield {exit_code!r}"
                    ),
                )
