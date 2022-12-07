"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

import cfnlint.core
from cfnlint.rules import CloudFormationLintRule, Match


class ErrorRule(CloudFormationLintRule):
    id = "E0000"
    description = "Error"


class WarningRule(CloudFormationLintRule):
    id = "W0000"
    description = "Warning"


class InformationRule(CloudFormationLintRule):
    id = "I0000"
    description = "Informational"


error_match = Match(0, 0, 0, 0, "", ErrorRule(), message="")
warning_match = Match(0, 0, 0, 0, "", WarningRule(), message="")
informational_match = Match(0, 0, 0, 0, "", InformationRule(), message="")


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
                match_names = [x.rule.description for x in matches]
                self.assertEqual(
                    cfnlint.core.get_exit_code(matches, level),
                    exit_code,
                    f"{match_names} matches with {level} level should yield {exit_code}",
                )
