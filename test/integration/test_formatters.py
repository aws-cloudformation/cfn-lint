"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import subprocess
from test.integration import BaseCliTestCase


class TestFormatters(BaseCliTestCase):
    """Test Formatters"""

    def test_junit(self):
        """Test JUnit formatting"""
        result = subprocess.check_output(
            [
                "cfn-lint",
                "--format",
                "junit",
                "--",
                "test/fixtures/templates/good/core/config_only_*.yaml",
            ]
        )

        if isinstance(result, bytes):
            result = result.decode("utf8")

        self.assertIn(
            (
                '<testcase name="I1002 Validate approaching the template size limit"'
                ' url="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"/>'
            ),
            result,
        )
        self.assertIn(
            (
                '<testcase name="I1003 Validate if we are approaching the '
                'max size of a description" '
                'url="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"/>'
            ),
            result,
        )

    def test_pretty(self):
        """Test pretty formatting"""
        result = subprocess.check_output(
            [
                "cfn-lint",
                "--format",
                "pretty",
                "--",
                "test/fixtures/templates/good/core/config_only_*.yaml",
            ]
        )

        if isinstance(result, bytes):
            result = result.decode("utf8")

        self.assertEqual(
            (
                "Cfn-lint scanned 2 templates against 2 rules and found 0 errors, 0"
                " warnings, and 0 informational violations"
            ),
            result.strip(),
        )
