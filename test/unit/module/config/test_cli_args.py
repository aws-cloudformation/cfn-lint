"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
import os
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
