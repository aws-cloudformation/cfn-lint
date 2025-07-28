"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
import os
import subprocess
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

import cfnlint.config  # pylint: disable=E0401

LOGGER = logging.getLogger("cfnlint")


class TestArgsParser(BaseTestCase):
    """Test Parser Arguments"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_create_parser(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            ["-t", "test.yaml", "--ignore-bad-template", "--format", "quiet", "--debug"]
        )
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(config.cli_args.template_alt, ["test.yaml"])
        self.assertEqual(config.cli_args.ignore_bad_template, True)
        self.assertEqual(config.cli_args.format, "quiet")
        self.assertEqual(config.cli_args.debug, True)

    def test_create_parser_default_param(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            [
                "--regions",
                "us-east-1",
                "us-west-2",
                "--",
                "template1.yaml",
                "template2.yaml",
            ]
        )
        self.assertEqual(
            config.cli_args.templates, ["template1.yaml", "template2.yaml"]
        )
        self.assertEqual(config.cli_args.template_alt, [])
        self.assertEqual(config.cli_args.regions, ["us-east-1", "us-west-2"])

    def test_stdout(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(["-t", "template1.yaml"])
        self.assertIsNone(config.cli_args.output_file)

    def test_output_file(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            ["-t", "template1.yaml", "--output-file", "test_output.txt"]
        )
        self.assertEqual(config.cli_args.output_file, "test_output.txt")

    def test_force_update_specs(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(["--update-specs", "--force"])
        self.assertEqual(config.cli_args.force, True)
        self.assertEqual(config.cli_args.update_specs, True)

    def test_create_parser_exend(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            ["-t", "template1.yaml", "-t", "template2.yaml"]
        )
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(
            config.cli_args.template_alt, ["template1.yaml", "template2.yaml"]
        )

    def test_create_parser_config_file_regions(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            [
                "--regions",
                "us-west-1",
                "--include-checks",
                "I1234",
                "--",
                "template1.yaml",
            ]
        )
        self.assertEqual(config.cli_args.templates, ["template1.yaml"])
        self.assertEqual(config.cli_args.include_checks, ["I1234"])
        self.assertEqual(config.cli_args.regions, ["us-west-1"])

    def test_create_parser_config_file(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            ["--mandatory-checks", "I1234", "--", "template1.yaml"]
        )
        self.assertEqual(config.cli_args.templates, ["template1.yaml"])
        self.assertEqual(config.cli_args.mandatory_checks, ["I1234"])

    def test_create_parser_rule_configuration(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            ["-x", "E3012:strict=true", "-x", "E3012:key=value,E3001:key=value"]
        )
        self.assertEqual(
            config.cli_args.configure_rules,
            {"E3012": {"key": "value", "strict": "true"}, "E3001": {"key": "value"}},
        )

    @patch("argparse.ArgumentParser.print_help")
    def test_bad_rule_configuration(self, mock_print_help):
        with self.assertRaises(SystemExit) as e:
            cfnlint.config.CliArgs(["-x", "E3012:key;value"])

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()

    def test_exit_code_parameter(self):
        """Test values of exit code"""

        for param in ["informational", "warning", "error"]:
            with self.subTest():
                config = cfnlint.config.CliArgs(["--non-zero-exit-code", param])
                self.assertEqual(config.cli_args.non_zero_exit_code, param)

    def test_exit_code_parameter_error(self):
        """Test result when bad value provided"""
        with open(os.devnull, "w") as devnull:
            with patch("sys.stderr", devnull):
                with self.assertRaises(SystemExit):
                    cfnlint.config.CliArgs(["--non-zero-exit-code", "bad"])
    
    def test_list_templates_none(self):
        """Test that --list-templates prints 'None' and exits cleanly"""

        args = ["--list-templates"]

        # Test the CLI argument parsing for --list-templates
        config = cfnlint.config.CliArgs(args)
        self.assertEqual(config.cli_args.listtemplates, True)
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(config.cli_args.template_alt, [])

        # Run cfn-lint and validate the output
        result = subprocess.run(
            ['cfn-lint', *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), 'None')

    def test_list_templates_files_only(self):
        """Test that --list-templates prints the file names"""

        args = [
            "--list-templates", 
            "-t", "test/fixtures/templates/public/lambda-poller.yaml",
            "-t", "test/fixtures/templates/public/rds-cluster.yaml"
        ]

        # Test the CLI argument parsing for --list-templates with multiple templates
        config = cfnlint.config.CliArgs(args)
        self.assertEqual(config.cli_args.listtemplates, True)
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(config.cli_args.template_alt, [
            "test/fixtures/templates/public/lambda-poller.yaml", 
            "test/fixtures/templates/public/rds-cluster.yaml"
        ])

        # Run cfn-lint and validate the output
        result = subprocess.run(
            ['cfn-lint', *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        expected_output = 'test/fixtures/templates/public/lambda-poller.yaml\ntest/fixtures/templates/public/rds-cluster.yaml'
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), expected_output)

    def test_list_templates_directories_only(self):
        """Test that --list-templates prints directory warnings"""

        pwd = os.getcwd()
        args = [
            "--list-templates", 
            "-t", pwd # Current directory
        ]

        # Test the CLI argument parsing for --list-templates with multiple templates
        config = cfnlint.config.CliArgs(args)
        self.assertEqual(config.cli_args.listtemplates, True)
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(config.cli_args.template_alt, [pwd])

        # Run cfn-lint and validate the output
        result = subprocess.run(
            ['cfn-lint', *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        expected_output = 'not a file: {}'.format(pwd)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), expected_output)

    def test_list_templates_files_and_directories(self):
        """Test that --list-templates prints file names and directory warnings"""
        
        template1 = "test/fixtures/templates/public/lambda-poller.yaml"
        template2 = "test/fixtures/templates/public/rds-cluster.yaml"
        pwd = os.getcwd()
        args = [
            "--list-templates", 
            "-t", template1,
            "-t", template2,
            "-t", pwd # Current directory
        ]

        # Test the CLI argument parsing for --list-templates with multiple templates
        config = cfnlint.config.CliArgs(args)
        self.assertEqual(config.cli_args.listtemplates, True)
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(config.cli_args.template_alt, [
            template1,
            template2,
            pwd
        ])

        # Run cfn-lint and validate the output
        result = subprocess.run(
            ['cfn-lint', *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        expected_output = f'not a file: {pwd}\n${template1}\n${template2}'
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), expected_output)
