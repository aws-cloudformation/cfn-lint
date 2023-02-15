"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

from six import StringIO

import cfnlint.config  # pylint: disable=E0401
import cfnlint.core  # pylint: disable=E0401

LOGGER = logging.getLogger("cfnlint")


class TestCli(BaseTestCase):
    """Test CLI processing"""

    def setUp(self):
        """Setup"""
        # Disable all but critical logger output, as both 'test_template_not_found' and
        # 'test_template_not_found_directory' like to print out errors to the console.
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Tear Down"""
        logging.disable(logging.NOTSET)
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_template_not_found(self):
        """Test template not found"""

        filename = "test/fixtures/templates/good/core/not_found.yaml"

        (args, filenames, _) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--ignore-bad-template"]
        )
        (_, _, matches) = cfnlint.core.get_template_rules(filenames[0], args)

        self.assertEqual(len(matches), 0)

    def test_template_not_found_directory(self):
        """Test template not found"""

        filename = "test/fixtures/templates/good/core"

        (args, filenames, _) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--ignore-bad-template"]
        )
        (_, _, matches) = cfnlint.core.get_template_rules(filenames[0], args)

        self.assertEqual(len(matches), 0)

    def test_template_invalid_yaml(self):
        """Test template not found"""
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"

        (args, filenames, _) = cfnlint.core.get_args_filenames(["--template", filename])
        (_, _, matches) = cfnlint.core.get_template_rules(filenames[0], args)

        self.assertEqual(len(matches), 1)

    def test_template_invalid_json(self):
        """Test template not found"""
        filename = "test/fixtures/templates/bad/core/config_invalid_json.json"

        (args, filenames, _) = cfnlint.core.get_args_filenames(["--template", filename])
        (_, _, matches) = cfnlint.core.get_template_rules(filenames[0], args)

        self.assertEqual(len(matches), 1)

    def test_template_invalid_yaml_ignore(self):
        """Test template not found"""
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"

        (args, filenames, _) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--ignore-bad-template"]
        )
        (_, _, matches) = cfnlint.core.get_template_rules(filenames[0], args)

        self.assertEqual(len(matches), 0)

    def test_template_invalid_yaml_ignore_by_rule_id(self):
        """Test template not found"""
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"

        (args, filenames, _) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--ignore-checks", "E0000"]
        )
        (_, _, matches) = cfnlint.core.get_template_rules(filenames[0], args)

        self.assertEqual(len(matches), 0)

    def test_template_invalid_json_ignore(self):
        """Test template not found"""
        filename = "test/fixtures/templates/bad/core/config_invalid_json.json"

        (args, filenames, _) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--ignore-bad-template"]
        )
        (_, _, matches) = cfnlint.core.get_template_rules(filenames[0], args)

        self.assertEqual(len(matches), 0)

    def test_template_via_stdin(self):
        """Test getting the template from stdin doesn't crash"""
        filename = "test/fixtures/templates/good/generic.yaml"
        with open(filename, "r") as fp:
            file_content = fp.read()

        with patch("sys.stdin", StringIO(file_content)):
            (_, filenames, _) = cfnlint.core.get_args_filenames([])
            assert filenames == [None]

        with patch("sys.stdin", StringIO(file_content)):
            (_, filenames, _) = cfnlint.core.get_args_filenames(
                ["--template", filename]
            )
            assert filenames == [filename]

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_template_config(self, yaml_mock):
        """Test template config"""
        yaml_mock.side_effect = [{}, {}]

        filename = "test/fixtures/templates/good/core/config_parameters.yaml"
        (
            args,
            _,
            _,
        ) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--ignore-bad-template"]
        )

        self.assertEqual(args.append_rules, [])
        self.assertEqual(args.append_rules, [])
        self.assertEqual(args.format, None)
        self.assertEqual(args.ignore_bad_template, True)
        self.assertEqual(args.ignore_checks, [])
        self.assertEqual(args.include_checks, ["W", "E"])
        self.assertEqual(args.listrules, False)
        self.assertEqual(args.debug, False)
        self.assertEqual(args.override_spec, None)
        self.assertEqual(args.custom_rules, None)
        self.assertEqual(args.regions, ["us-east-1"])
        self.assertEqual(
            args.templates, ["test/fixtures/templates/good/core/config_parameters.yaml"]
        )
        self.assertEqual(args.update_documentation, False)
        self.assertEqual(args.update_specs, False)
        self.assertEqual(args.output_file, None)

    def test_output_file(self):
        filename = "test/fixtures/templates/good/core/config_parameters.yaml"
        (
            args,
            _,
            _,
        ) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--output-file", "test_output.txt"]
        )

        self.assertEqual(args.output_file, "test_output.txt")

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_positional_template_parameters(self, yaml_mock):
        """Test overriding parameters"""
        yaml_mock.side_effect = [{}, {}]

        filename = "test/fixtures/templates/good/core/config_parameters.yaml"
        (args, _, _) = cfnlint.core.get_args_filenames(
            [filename, "--ignore-bad-template", "--ignore-checks", "E0000"]
        )

        self.assertEqual(args.append_rules, [])
        self.assertEqual(args.format, None)
        self.assertEqual(args.ignore_bad_template, True)
        self.assertEqual(args.ignore_checks, ["E0000"])
        self.assertEqual(args.include_checks, ["W", "E"])
        self.assertEqual(args.listrules, False)
        self.assertEqual(args.debug, False)
        self.assertEqual(args.override_spec, None)
        self.assertEqual(args.custom_rules, None)
        self.assertEqual(args.regions, ["us-east-1"])
        self.assertEqual(
            args.templates, ["test/fixtures/templates/good/core/config_parameters.yaml"]
        )
        self.assertEqual(args.update_documentation, False)
        self.assertEqual(args.update_specs, False)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_override_parameters(self, yaml_mock):
        """Test overriding parameters"""
        yaml_mock.side_effect = [{}, {}]

        filename = "test/fixtures/templates/good/core/config_parameters.yaml"
        (args, _, _) = cfnlint.core.get_args_filenames(
            [
                "--template",
                filename,
                "--ignore-bad-template",
                "--ignore-checks",
                "E0000",
            ]
        )

        self.assertEqual(args.append_rules, [])
        self.assertEqual(args.format, None)
        self.assertEqual(args.ignore_bad_template, True)
        self.assertEqual(args.ignore_checks, ["E0000"])
        self.assertEqual(args.include_checks, ["W", "E"])
        self.assertEqual(args.listrules, False)
        self.assertEqual(args.debug, False)
        self.assertEqual(args.override_spec, None)
        self.assertEqual(args.custom_rules, None)
        self.assertEqual(args.regions, ["us-east-1"])
        self.assertEqual(
            args.templates, ["test/fixtures/templates/good/core/config_parameters.yaml"]
        )
        self.assertEqual(args.update_documentation, False)
        self.assertEqual(args.update_specs, False)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_bad_config(self, yaml_mock):
        """Test bad formatting in config"""
        yaml_mock.side_effect = [{}, {}]

        filename = "test/fixtures/templates/bad/core/config_parameters.yaml"
        (args, _, _) = cfnlint.core.get_args_filenames(
            ["--template", filename, "--ignore-bad-template"]
        )

        self.assertEqual(args.append_rules, [])
        self.assertEqual(args.format, None)
        self.assertEqual(args.ignore_bad_template, True)
        self.assertEqual(args.ignore_checks, [])
        self.assertEqual(args.include_checks, ["W", "E"])
        self.assertEqual(args.listrules, False)
        self.assertEqual(args.debug, False)
        self.assertEqual(args.override_spec, None)
        self.assertEqual(args.custom_rules, None)
        self.assertEqual(args.regions, ["us-east-1"])
        self.assertEqual(args.templates, [filename])
        self.assertEqual(args.update_documentation, False)
        self.assertEqual(args.update_specs, False)
