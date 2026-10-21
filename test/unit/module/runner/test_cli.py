"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
import os
import tempfile
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
        mock_maintenance.return_value = 0
        config = ConfigMixIn(["--update-specs"])

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)
        mock_maintenance.assert_called_once_with(False)

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

    @patch("cfnlint.runner.cli.ConfigMixIn")
    def test_main_config_file_error_none_config(self, mock_config):
        from cfnlint.exceptions import ConfigFileError
        from cfnlint.runner.cli import main

        mock_config.side_effect = ConfigFileError("Invalid key 'bad'", None)

        with patch("sys.exit", side_effect=SystemExit(1)):
            with patch("builtins.print") as mock_print:
                with self.assertRaises(SystemExit):
                    main()
                mock_print.assert_called_once_with("Invalid key 'bad'")


class TestCliConvert(BaseTestCase):
    """Test --convert with config"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    @patch("sys.stdout", new_callable=StringIO)
    def test_convert_json(self, mock_stdout):
        config = ConfigMixIn(
            [
                "--convert",
                "json",
                "--template",
                "test/fixtures/templates/good/generic.yaml",
            ]
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)

        template = json.loads(mock_stdout.getvalue())
        self.assertIn("Resources", template)
        # short form functions are written out in their long form
        self.assertEqual(
            {"Ref": "RootInstanceProfile"},
            template["Resources"]["MyEC2Instance"]["Properties"]["IamInstanceProfile"],
        )

    def test_convert_json_to_output_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output_file = os.path.join(directory, "generic.json")
            config = ConfigMixIn(
                [
                    "--convert",
                    "json",
                    "--output-file",
                    output_file,
                    "--template",
                    "test/fixtures/templates/good/generic.yaml",
                ]
            )

            runner = Runner(config)

            with self.assertRaises(SystemExit) as e:
                runner.cli()

            self.assertEqual(e.exception.code, 0)

            with open(output_file) as f:
                self.assertIn("Resources", json.load(f))

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_convert_json_bad_template(self, mock_stdout, mock_stderr):
        config = ConfigMixIn(
            [
                "--convert",
                "json",
                "--template",
                "test/fixtures/templates/bad/core/config_invalid_yaml.yaml",
            ]
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 2)
        # stdout stays clean so it can be redirected into a file
        self.assertEqual("", mock_stdout.getvalue())
        self.assertIn("E0000", mock_stderr.getvalue())

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_convert_json_unserializable_value(self, mock_stdout, mock_stderr):
        """A value with no JSON equivalent is reported, not raised"""
        with tempfile.TemporaryDirectory() as directory:
            template = os.path.join(directory, "binary.yaml")
            with open(template, "w") as f:
                f.write("Resources:\n  Bucket:\n    Type: !!binary R0lGODlh\n")

            config = ConfigMixIn(["--convert", "json", "--template", template])

            runner = Runner(config)

            with self.assertRaises(SystemExit) as e:
                runner.cli()

            self.assertEqual(e.exception.code, 2)
            self.assertEqual("", mock_stdout.getvalue())
            self.assertIn("cannot be written as JSON", mock_stderr.getvalue())

    @patch("sys.stderr", new_callable=StringIO)
    def test_convert_json_multiple_templates(self, mock_stderr):
        config = ConfigMixIn(
            [
                "--convert",
                "json",
                "--template",
                "test/fixtures/templates/good/generic.yaml",
                "test/fixtures/templates/good/minimal.yaml",
            ]
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        self.assertIn("needs one template, found 2", mock_stderr.getvalue())

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdin.isatty")
    def test_convert_json_template_resolves_to_nothing(self, mock_isatty, mock_stderr):
        """A template that matches no file is not an invitation to read stdin"""
        mock_isatty.return_value = False

        config = ConfigMixIn(
            [
                "--convert",
                "json",
                "--ignore-bad-template",
                "--template",
                "test/fixtures/templates/dne/*.yaml",
            ]
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        self.assertIn("needs one template, found 0", mock_stderr.getvalue())

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdin.isatty")
    def test_convert_json_with_deployment_files(self, mock_isatty, mock_stderr):
        """Deployment files would otherwise be dropped in favor of stdin"""
        mock_isatty.return_value = False

        config = ConfigMixIn(
            ["--convert", "json"],
            deployment_files=["test/fixtures/templates/good/generic.yaml"],
        )

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 1)
        self.assertIn("cannot be used with deployment files", mock_stderr.getvalue())

    @patch("sys.stdout", new_callable=StringIO)
    @patch("fileinput.input")
    @patch("sys.stdin.isatty")
    def test_convert_json_from_stdin(self, mock_isatty, mock_fileinput, mock_stdout):
        mock_fileinput.return_value = StringIO(
            "Resources:\n  Bucket:\n    Type: AWS::S3::Bucket\n"
        )
        mock_isatty.return_value = False

        config = ConfigMixIn(["--convert", "json"])

        runner = Runner(config)

        with self.assertRaises(SystemExit) as e:
            runner.cli()

        self.assertEqual(e.exception.code, 0)
        self.assertEqual(
            {"Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}}},
            json.loads(mock_stdout.getvalue()),
        )
