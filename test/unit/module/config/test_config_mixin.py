"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
import os
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

import cfnlint.config
from cfnlint.context import ParameterSet
from cfnlint.helpers import REGIONS

LOGGER = logging.getLogger("cfnlint")


class TestConfigMixIn(BaseTestCase):
    """Test ConfigParser Arguments"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_mix_in(self, yaml_mock):
        """Test mix in"""
        yaml_mock.side_effect = [
            {"include_checks": ["I", "I1111"], "regions": ["us-west-2"]},
            {},
        ]

        config = cfnlint.config.ConfigMixIn(["--regions", "us-west-1"])
        self.assertEqual(config.regions, ["us-west-1"])
        self.assertEqual(config.include_checks, ["W", "E", "I", "I1111"])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_precedence(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [
            {
                "include_checks": ["I"],
                "ignore_checks": ["E3001"],
                "regions": ["us-west-2"],
            },
            {},
        ]
        config = cfnlint.config.ConfigMixIn(["--include-checks", "I1234", "I4321"])
        config.template_args = {
            "Metadata": {
                "cfn-lint": {
                    "config": {"include_checks": ["I9876"], "ignore_checks": ["W3001"]}
                }
            }
        }
        # config files wins
        self.assertEqual(config.regions, ["us-west-2"])
        # CLI should win
        self.assertEqual(config.include_checks, ["W", "E", "I1234", "I4321"])
        # template file wins over config file
        self.assertEqual(config.ignore_checks, ["W3001"])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_file_output(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{"output_file": "test_output.txt"}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # Config file wins
        self.assertEqual(config.output_file, "test_output.txt")

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_file_output_mixin(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{"output_file": "test_output.txt"}, {}]
        config = cfnlint.config.ConfigMixIn(["--output-file", "test_output_2.txt"])

        # CLI args win
        self.assertEqual(config.output_file, "test_output_2.txt")

    @patch.dict(
        os.environ,
        {
            "HOME": os.environ.get("HOME", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "HOMEPATH": os.environ.get("HOMEPATH", ""),
            "HOMEDRIVE": os.environ.get("HOMEDRIVE", ""),
        },
        clear=True,
    )
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_default_region(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, ["us-east-1"])

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
            "AWS_DEFAULT_REGION": "us-west-1",
            "HOME": os.environ.get("HOME", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "HOMEPATH": os.environ.get("HOMEPATH", ""),
            "HOMEDRIVE": os.environ.get("HOMEDRIVE", ""),
        },
        clear=True,
    )
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_region_from_AWS_REGION_envvar(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, ["us-west-2"])

    @patch.dict(
        os.environ,
        {
            "AWS_DEFAULT_REGION": "us-west-1",
            "HOME": os.environ.get("HOME", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "HOMEPATH": os.environ.get("HOMEPATH", ""),
            "HOMEDRIVE": os.environ.get("HOMEDRIVE", ""),
        },
        clear=True,
    )
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_region_from_AWS_DEFAULT_REGION_envvar(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, ["us-west-1"])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_all_regions(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{"regions": ["ALL_REGIONS"]}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, REGIONS)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_force_with_update_specs(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn(["--update-specs", "--force"])

        # test defaults
        self.assertEqual(config.force, True)
        self.assertEqual(config.update_specs, True)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    @patch("sys.stdin.isatty", return_va=True)
    def test_config_expand_paths(self, isatty_mock, yaml_mock):
        """Test precedence in"""
        isatty_mock.return_value = True
        yaml_mock.side_effect = [
            {"templates": ["test/fixtures/templates/public/*.yaml"]},
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(
            config.templates,
            [
                str(
                    Path(
                        "test/fixtures/templates/public"
                        + os.path.sep
                        + "lambda-poller.yaml"
                    )
                ),
                str(
                    Path(
                        "test/fixtures/templates/public"
                        + os.path.sep
                        + "rds-cluster.yaml"
                    )
                ),
            ],
        )

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    @patch("sys.stdin.isatty", return_va=True)
    def test_config_expand_paths_nomatch(self, isatty_mock, yaml_mock):
        """Test precedence in"""

        filename = "test/fixtures/templates/nonexistant/*.yaml"
        isatty_mock.return_value = True
        yaml_mock.side_effect = [
            {"templates": [filename]},
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        with self.assertRaises(ValueError):
            self.assertEqual(len(config.templates), 1)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    @patch("sys.stdin.isatty", return_va=True)
    def test_config_expand_paths_nomatch_ignore_bad_template(
        self, isatty_mock, yaml_mock
    ):
        """Test precedence in"""

        filename = "test/fixtures/templates/nonexistant/*.yaml"
        isatty_mock.return_value = True
        yaml_mock.side_effect = [
            {"templates": [filename], "ignore_bad_template": True},
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.templates, [])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    @patch("sys.stdin.isatty", return_va=True)
    def test_config_expand_ignore_templates(self, isatty_mock, yaml_mock):
        """Test ignore templates"""
        isatty_mock.return_value = True
        yaml_mock.side_effect = [
            {
                "templates": ["test/fixtures/templates/bad/resources/iam/*.yaml"],
                "ignore_templates": [
                    "test/fixtures/templates/bad/resources/iam/resource_*.yaml"
                ],
            },
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertNotIn(
            str(Path("test/fixtures/templates/bad/resources/iam/resource_policy.yaml")),
            config.templates,
        )
        self.assertEqual(len(config.templates), 3)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    @patch("sys.stdin.isatty", return_va=True)
    def test_config_expand_and_ignore_templates_with_bad_path(
        self, isatty_mock, yaml_mock
    ):
        """Test ignore templates"""

        isatty_mock.return_value = True
        yaml_mock.side_effect = [
            {
                "templates": ["test/fixtures/templates/bad/resources/iam/*.yaml"],
                "ignore_templates": [
                    "dne/fixtures/templates/bad/resources/iam/resource_*.yaml"
                ],
            },
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertIn(
            str(Path("test/fixtures/templates/bad/resources/iam/resource_policy.yaml")),
            config.templates,
        )
        self.assertEqual(len(config.templates), 4)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    @patch("sys.stdin.isatty", return_va=True)
    def test_config_merge(self, isatty_mock, yaml_mock):
        """Test merging lists"""

        isatty_mock.return_value = True
        yaml_mock.side_effect = [
            {
                "include_checks": ["I"],
                "ignore_checks": ["E3001"],
                "regions": ["us-west-2"],
            },
            {},
        ]
        config = cfnlint.config.ConfigMixIn(
            ["--include-checks", "I1234", "I4321", "--merge-configs"]
        )
        config.template_args = {
            "Metadata": {
                "cfn-lint": {
                    "config": {"include_checks": ["I9876"], "ignore_checks": ["W3001"]}
                }
            }
        }
        # config files wins
        self.assertEqual(config.regions, ["us-west-2"])
        # CLI should win
        self.assertEqual(
            config.include_checks, ["W", "E", "I1234", "I4321", "I9876", "I"]
        )
        # template file wins over config file
        self.assertEqual(config.ignore_checks, ["W3001", "E3001"])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_parameters(self, yaml_mock):
        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn(["--parameters", "Foo=Bar"])

        # test defaults
        self.assertEqual(getattr(config.cli_args, "parameters"), [{"Foo": "Bar"}])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_parameters_lists(self, yaml_mock):
        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn(["--parameters", "A=1", "B=2"])

        # test defaults
        self.assertEqual(getattr(config.cli_args, "parameters"), [{"A": "1", "B": "2"}])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_parameters_lists_bad_value(self, yaml_mock):
        yaml_mock.side_effect = [{}, {}]

        with patch("sys.exit") as exit:
            cfnlint.config.ConfigMixIn(
                [
                    "--parameters",
                    "A",
                ]
            )
            exit.assert_called_once_with(1)

    @patch("glob.glob")
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_template_deployment_files(self, yaml_mock, glob_mock):
        _filenames = ["one.yaml"]
        yaml_mock.side_effect = [{}, {}]
        glob_mock.side_effect = [_filenames]
        config = cfnlint.config.ConfigMixIn(["--deployment-files", "*.yaml"])

        self.assertEqual(config.deployment_files, _filenames)
        glob_mock.assert_called_once()

    @patch("glob.glob")
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_template_parameter_files(self, yaml_mock, glob_mock):
        _filenames = ["one.json"]
        yaml_mock.side_effect = [{}, {}]

        glob_mock.side_effect = [_filenames]
        config = cfnlint.config.ConfigMixIn(["--parameter-files", "*.json"])

        self.assertEqual(config.parameter_files, _filenames)
        glob_mock.assert_called_once()

    @patch("argparse.ArgumentParser.print_help")
    def test_templates_with_deployment_files(self, mock_print_help):
        with self.assertRaises(SystemExit) as e:
            cfnlint.config.ConfigMixIn(
                [
                    "--deployment-files",
                    "test/fixtures/templates/good/generic.yaml",
                    "--template",
                    "test/fixtures/templates/good/generic.yaml",
                ]
            )

        self.assertEqual(e.exception.code, 1)
        mock_print_help.assert_called_once()

    def test_conversion_of_template_parameters(self):
        config = cfnlint.ConfigMixIn(["--parameters", "Foo=Bar"])

        self.assertEqual(
            config.parameters, [ParameterSet(source=None, parameters={"Foo": "Bar"})]
        )

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_compares(self, yaml_mock):
        yaml_mock.side_effect = [{}, {}, {}, {}]
        config1 = cfnlint.config.ConfigMixIn(
            ["--template", "test/fixtures/templates/good/generic.yaml"]
        )
        config2 = cfnlint.config.ConfigMixIn(
            ["--template", "test/fixtures/templates/bad/generic.yaml"]
        )

        self.assertNotEqual(config1, 1)
        self.assertNotEqual(config1, config2)


class TestConfigMixInValidation(BaseTestCase):
    """Test ConfigMixIn validation functionality"""

    def test_validate_no_templates_or_deployment_files(self):
        """Test validation fails when no templates or deployment files are specified"""
        config = cfnlint.config.ConfigMixIn()

        with self.assertRaises(ValueError) as context:
            config.validate()  # Don't allow stdin for API usage

        self.assertIn(
            "No templates or deployment files specified", str(context.exception)
        )

    def test_validate_no_templates_or_deployment_files_with_stdin_allowed(self):
        """Test validation passes when no templates/deployment files but stdin is
        allowed"""
        config = cfnlint.config.ConfigMixIn()

        # Should not raise any exception when stdin is allowed
        try:
            config.validate(allow_stdin=True)
        except ValueError:
            self.fail("validate(allow_stdin=True) raised ValueError unexpectedly!")

    def test_validate_with_positional_templates_argument(self):
        """Test validation works with positional templates argument
        (covers elif cli_args branch)"""
        # This tests the elif cli_args: branch in validate method (line 824)
        config = cfnlint.config.ConfigMixIn(
            ["template.yaml"]
        )  # Positional argument goes to templates, not template_alt

        # Should not raise any exception for valid config
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_with_string_template_conversion(self):
        """Test validation converts string template to list (covers line 828)"""
        # This tests the string to list conversion logic (line 828)
        config = cfnlint.config.ConfigMixIn(
            templates="single_template.yaml"
        )  # Single string template

        # Should not raise any exception and should handle string conversion
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_deployment_files_with_templates(self):
        """Test validation fails when deployment files are used with templates"""
        config = cfnlint.config.ConfigMixIn(
            deployment_files=["deployment.yaml"], templates=["template.yaml"]
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn("Deployment files cannot be used with", str(context.exception))

    def test_validate_deployment_files_with_parameters(self):
        """Test validation fails when deployment files are used with parameters"""
        config = cfnlint.config.ConfigMixIn(
            deployment_files=["deployment.yaml"], parameters={"Key": "Value"}
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn("Deployment files cannot be used with", str(context.exception))

    def test_validate_deployment_files_with_parameter_files(self):
        """Test validation fails when deployment files are used with parameter files"""
        config = cfnlint.config.ConfigMixIn(
            deployment_files=["deployment.yaml"], parameter_files=["params.json"]
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn("Deployment files cannot be used with", str(context.exception))

    def test_validate_parameters_and_parameter_files(self):
        """Test validation fails when both parameters and parameter files are
        specified"""
        config = cfnlint.config.ConfigMixIn(
            templates=["template.yaml"],
            parameters={"Key": "Value"},
            parameter_files=["params.json"],
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn(
            "Cannot specify both --parameters and --parameter-files",
            str(context.exception),
        )

    def test_validate_multiple_templates_with_parameters(self):
        """Test validation fails when parameters are used with multiple templates"""
        config = cfnlint.config.ConfigMixIn(
            templates=["template1.yaml", "template2.yaml"], parameters={"Key": "Value"}
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn(
            "Parameters can only be used with a single template", str(context.exception)
        )

    def test_validate_multiple_templates_with_parameter_files(self):
        """Test validation fails when parameter files are used with multiple
        templates"""
        config = cfnlint.config.ConfigMixIn(
            templates=["template1.yaml", "template2.yaml"],
            parameter_files=["params.json"],
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn(
            "Parameters can only be used with a single template", str(context.exception)
        )

    def test_validate_cli_template_with_manual_deployment_files(self):
        """Test validation fails when CLI template conflicts with manual
        deployment files"""
        config = cfnlint.config.ConfigMixIn(
            [
                "--template",
                "test/fixtures/templates/good/generic.yaml",
            ],
            deployment_files=[
                "test/fixtures/templates/good/generic.yaml",
            ],
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn("Deployment files cannot be used with", str(context.exception))

    def test_validate_valid_configuration_with_templates(self):
        """Test validation passes with valid template configuration"""
        config = cfnlint.config.ConfigMixIn(templates=["template.yaml"])

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_deployment_files(self):
        """Test validation passes with valid deployment files configuration"""
        config = cfnlint.config.ConfigMixIn(deployment_files=["deployment.yaml"])

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_single_template_and_parameters(self):
        """Test validation passes with single template and parameters"""
        config = cfnlint.config.ConfigMixIn(
            templates=["template.yaml"], parameters={"Key": "Value"}
        )

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_single_template_and_parameter_files(
        self,
    ):
        """Test validation passes with single template and parameter files"""
        config = cfnlint.config.ConfigMixIn(
            templates=["template.yaml"], parameter_files=["params.json"]
        )

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_multiple_templates_no_parameters(self):
        """Test validation passes with multiple templates and no parameters"""
        config = cfnlint.config.ConfigMixIn(
            templates=["template1.yaml", "template2.yaml"]
        )

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")
