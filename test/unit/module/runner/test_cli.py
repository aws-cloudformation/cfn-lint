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
        # isatty should be called at least once
        self.assertTrue(mock_isatty.call_count >= 1)
        # self.assertEqual(mock_isatty.call_count, 2)

    @patch("argparse.ArgumentParser.print_help")
    @patch("sys.stdin.isatty")
    def test_no_templates_no_deployment_files(self, mock_isatty, mock_print_help):
        """Test that help is printed when no templates or deployment
        files are provided and stdin is a tty"""
        # Create a config with no templates or deployment files
        config = ConfigMixIn([])

        # Ensure templates and deployment_files are empty or None
        self.assertTrue(not config.templates or config.templates == [])
        self.assertTrue(not config.deployment_files or config.deployment_files == [])

        runner = Runner(config)
        mock_isatty.return_value = True

        # Should exit with code 1 and print help
        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()
        # isatty should be called at least once
        self.assertTrue(mock_isatty.call_count >= 1)

    @patch("argparse.ArgumentParser.print_help")
    @patch("sys.stdin.isatty")
    @patch("cfnlint.runner.Runner._cli_output")
    def test_no_templates_no_deployment_files_with_stdin(
        self, mock_cli_output, mock_isatty, mock_print_help
    ):
        """Test that when no templates or deployment files are
        provided but stdin is not a tty, the program continues
        execution without printing help"""
        # Create a config with no templates or deployment files
        config = ConfigMixIn([])

        # Ensure templates and deployment_files are empty or None
        self.assertTrue(not config.templates or config.templates == [])
        self.assertTrue(not config.deployment_files or config.deployment_files == [])

        # Mock _cli_output to avoid actual processing
        mock_cli_output.return_value = None

        runner = Runner(config)
        mock_isatty.return_value = False

        # Should not exit and not print help
        runner.cli()

        # Help should not be printed
        mock_print_help.assert_not_called()
        # isatty should be called at least once
        self.assertTrue(mock_isatty.call_count >= 1)
        # _cli_output should be called once
        mock_cli_output.assert_called_once()

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
