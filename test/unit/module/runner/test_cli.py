"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

from cfnlint import ConfigMixIn
from cfnlint.runner import Runner

LOGGER = logging.getLogger("cfnlint")


class TestCli(BaseTestCase):
    """Test CLI with config"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    @patch("cfnlint.maintenance.update_documentation")
    def test_update_documentation(self, mock_maintenance):
        config = ConfigMixIn(["--update-documentation"])

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)
        mock_maintenance.assert_called_once()

    @patch("cfnlint.maintenance.update_resource_specs")
    def test_update_specs(self, mock_maintenance):
        config = ConfigMixIn(["--update-specs"])

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)
        mock_maintenance.assert_called_once()

    @patch("cfnlint.maintenance.update_iam_policies")
    def test_update_iam_policies(self, mock_maintenance):
        config = ConfigMixIn(["--update-iam-policies"])

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)
        mock_maintenance.assert_called_once()

    def test_list_rules(self):
        config = ConfigMixIn(["--list-rules"])

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)

    @patch("argparse.ArgumentParser.print_help")
    @patch("sys.stdin.isatty")
    def test_print_help(self, mock_isatty, mock_print_help):
        config = ConfigMixIn([])

        runner = Runner(config)
        mock_isatty.return_value = True
        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()
        mock_isatty.assert_called_once()

    def test_bad_regions(self):
        config = ConfigMixIn(
            [
                "--regions",
                "us-north-5",
                "--template",
                "test/fixtures/templates/good/generic.yaml",
            ]
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 32)
