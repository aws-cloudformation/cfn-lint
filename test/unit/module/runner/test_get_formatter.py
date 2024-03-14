"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

import cfnlint.formatters
from cfnlint import ConfigMixIn
from cfnlint.runner import get_formatter


class TestGetFormatter(BaseTestCase):
    """Test get formatter with config"""

    def test_basic(self):
        config = ConfigMixIn([])
        formatter = get_formatter(config)

        self.assertIsInstance(formatter, cfnlint.formatters.Formatter)

    def test_json(self):
        config = ConfigMixIn(["--format", "json"])
        formatter = get_formatter(config)

        self.assertIsInstance(formatter, cfnlint.formatters.JsonFormatter)

    def test_quiet(self):
        config = ConfigMixIn(["--format", "quiet"])
        formatter = get_formatter(config)

        self.assertIsInstance(formatter, cfnlint.formatters.QuietFormatter)

    def test_parseable(self):
        config = ConfigMixIn(["--format", "parseable"])
        formatter = get_formatter(config)

        self.assertIsInstance(formatter, cfnlint.formatters.ParseableFormatter)

    def test_junit(self):
        config = ConfigMixIn(["--format", "junit"])
        formatter = get_formatter(config)

        self.assertIsInstance(formatter, cfnlint.formatters.JUnitFormatter)

    def test_pretty(self):
        config = ConfigMixIn(["--format", "pretty"])
        formatter = get_formatter(config)

        self.assertIsInstance(formatter, cfnlint.formatters.PrettyFormatter)

    def test_sarif(self):
        config = ConfigMixIn(["--format", "sarif"])
        formatter = get_formatter(config)

        self.assertIsInstance(formatter, cfnlint.formatters.SARIFFormatter)
