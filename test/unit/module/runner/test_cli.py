"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from io import StringIO
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

from cfnlint import ConfigMixIn
from cfnlint.helpers import format_json_string
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

    @patch("cfnlint.maintenance.patch_resource_specs")
    def test_patch_specs(self, mock_maintenance):
        config = ConfigMixIn(["--patch-specs"])

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
        # self.assertEqual(mock_isatty.call_count, 2)

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

    @patch("argparse.ArgumentParser.print_help")
    def test_templates_with_deployment_files(self, mock_print_help):

        config = ConfigMixIn(
            [
                "--template",
                "test/fixtures/templates/good/generic.yaml",
            ],
            deployment_files=[
                "test/fixtures/templates/good/generic.yaml",
            ],
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()

    @patch("argparse.ArgumentParser.print_help")
    def test_templates_with_parameters_and_parameter_files(self, mock_print_help):

        config = ConfigMixIn(
            [
                "--template",
                "test/fixtures/templates/good/generic.yaml",
            ],
            parameters=[
                {"foo": "bar"},
            ],
            parameter_files=["test/fixtures/parameter_files/*.json"],
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()

    @patch("argparse.ArgumentParser.print_help")
    def test_templates_with_deployment_files_and_parameters(self, mock_print_help):

        config = ConfigMixIn(
            [],
            parameters=[
                {"foo": "bar"},
            ],
            deployment_files=["test/fixtures/parameter_files/*.json"],
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()

    @patch("argparse.ArgumentParser.print_help")
    def test_templates_with_parameters_and_multiple_templates(self, mock_print_help):

        config = ConfigMixIn(
            [
                "--template",
                "test/fixtures/templates/good/generic.yaml",
                "test/fixtures/templates/good/generic.yaml",
            ],
            parameters=[
                {"foo": "bar"},
            ],
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()

    @patch("fileinput.input")
    @patch("sys.stdin.isatty")
    def test_templates_with_stdin(self, mock_isatty, mock_fileinput):
        template = {
            "Resources": {
                "Bucket": {
                    "Type": "AWS::S3::Bucket",
                }
            }
        }

        mock_fileinput.return_value = StringIO(format_json_string(template))
        mock_isatty.return_value = False

        config = ConfigMixIn()

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)

    @patch("fileinput.input")
    @patch("sys.stdin.isatty")
    def test_templates_with_stdin_with_bad_syntax(self, mock_isatty, mock_fileinput):
        template = "{"

        mock_fileinput.return_value = StringIO(template)
        mock_isatty.return_value = False

        config = ConfigMixIn()

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 2)
