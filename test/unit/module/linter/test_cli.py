"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import jsonschema
from test.testlib.testcase import BaseTestCase
from six import StringIO
from mock import patch, mock
import cfnlint.config  # pylint: disable=E0401
LOGGER = logging.getLogger('cfnlint')


class error(cfnlint.rules.CloudFormationLintRule):
    """ basic rule for testing """
    id = 'E0000'


class warning(cfnlint.rules.CloudFormationLintRule):
    """ basic rule for testing """
    id = 'W0000'


class info(cfnlint.rules.CloudFormationLintRule):
    """ basic rule for testing """
    id = 'I0000'


class TestCli(BaseTestCase):
    """Test CLI processing """
    filename = 'test.yaml'
    match_error = cfnlint.rules.Match(1, 1, 1, 1, filename, error, 'error')
    match_warning = cfnlint.rules.Match(1, 1, 1, 1, filename, warning, 'warning')
    match_info = cfnlint.rules.Match(1, 1, 1, 1, filename, info, 'warning')

    def setUp(self):
        """ setup some basic options """
        super(TestCli, self).setUp()

        with patch('cfnlint.config.ConfigFileArgs._read_config', return_value={}):
            with patch('cfnlint.rules.RulesCollection.create_from_directory'):
                self.linter = cfnlint.CliLinter([])
                self.linter.all_rules.extend([error, warning, info])

    def tearDown(self):
        """ Tear Down """
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_template_via_stdin(self):
        """Test getting the template from stdin doesn't crash"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        with open(filename, 'r') as fp:
            file_content = fp.read()

        with patch('sys.stdin', StringIO(file_content)):
            linter = cfnlint.CliLinter([])
            self.assertIsNone(linter.config.templates)

        with patch('sys.stdin', StringIO(file_content)):
            linter = cfnlint.CliLinter([filename])
            self.assertEqual(linter.config.templates, [filename])

    # @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    # def test_template_config(self, yaml_mock):
    #    """Test template config"""
    #    yaml_mock.side_effect = [
    #        {},
    #        {}
    #    ]
#
    #    filename = 'test/fixtures/templates/good/core/config_parameters.yaml'
    #    linter = cfnlint.CliLinter(['--template', filename, '--ignore-bad-template'])
#
    #    self.assertEqual(len(linter.config.append_rules), 1)
    #    self.assertEqual(linter.config.format, None)
    #    self.assertEqual(linter.config.ignore_bad_template, True)
    #    self.assertEqual(linter.config.ignore_checks, [])
    #    self.assertEqual(linter.config.include_checks, ['E', 'W', ])
    #    self.assertEqual(linter.config.listrules, False)
    #    self.assertEqual(linter.config.debug, False)
    #    self.assertEqual(linter.config.override_spec, None)
    #    self.assertEqual(linter.config.regions, ['us-east-1'])
    #    self.assertEqual(
    #        linter.config.templates, [
    #            'test/fixtures/templates/good/core/config_parameters.yaml'])
    #    self.assertEqual(linter.config.update_documentation, False)
    #    self.assertEqual(linter.config.update_specs, False)
#
    # @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    # def test_positional_template_parameters(self, yaml_mock):
    #    """Test overriding parameters"""
    #    yaml_mock.side_effect = [
    #        {},
    #        {}
    #    ]
#
    #    filename = 'test/fixtures/templates/good/core/config_parameters.yaml'
    #    linter = cfnlint.CliLinter([
    #        filename, '--ignore-bad-template',
    #        '--ignore-checks', 'E0000'])
#
    #    self.assertEqual(len(linter.config.append_rules), 1)
    #    self.assertEqual(linter.config.format, None)
    #    self.assertEqual(linter.config.ignore_bad_template, True)
    #    self.assertEqual(linter.config.ignore_checks, ['E0000'])
    #    self.assertEqual(linter.config.include_checks, ['E', 'W', ])
    #    self.assertEqual(linter.config.listrules, False)
    #    self.assertEqual(linter.config.debug, False)
    #    self.assertEqual(linter.config.override_spec, None)
    #    self.assertEqual(linter.config.regions, ['us-east-1'])
    #    self.assertEqual(
    #        linter.config.templates, [
    #            'test/fixtures/templates/good/core/config_parameters.yaml'])
    #    self.assertEqual(linter.config.update_documentation, False)
    #    self.assertEqual(linter.config.update_specs, False)
#
    # @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    # def test_override_parameters(self, yaml_mock):
    #    """Test overriding parameters"""
    #    yaml_mock.side_effect = [
    #        {},
    #        {}
    #    ]
#
    #    filename = 'test/fixtures/templates/good/core/config_parameters.yaml'
    #    linter = cfnlint.CliLinter([
    #        '--template', filename, '--ignore-bad-template',
    #        '--ignore-checks', 'E0000'])
#
    #    self.assertEqual(len(linter.config.append_rules), 1)
    #    self.assertEqual(linter.config.format, None)
    #    self.assertEqual(linter.config.ignore_bad_template, True)
    #    self.assertEqual(linter.config.ignore_checks, ['E0000'])
    #    self.assertEqual(linter.config.include_checks, ['E', 'W', ])
    #    self.assertEqual(linter.config.listrules, False)
    #    self.assertEqual(linter.config.debug, False)
    #    self.assertEqual(linter.config.override_spec, None)
    #    self.assertEqual(linter.config.regions, ['us-east-1'])
    #    self.assertEqual(
    #        linter.config.templates, [
    #            'test/fixtures/templates/good/core/config_parameters.yaml'])
    #    self.assertEqual(linter.config.update_documentation, False)
    #    self.assertEqual(linter.config.update_specs, False)
#
    # @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    # def test_bad_config(self, yaml_mock):
    #    """ Test bad formatting in config"""
    #    yaml_mock.side_effect = [
    #        {},
    #        {}
    #    ]
#
    #    filename = 'test/fixtures/templates/bad/core/config_parameters.yaml'
    #    linter = cfnlint.CliLinter([
    #        '--template', filename, '--ignore-bad-template'])
#
    #    self.assertEqual(len(linter.config.append_rules), 1)
    #    self.assertEqual(linter.config.format, None)
    #    self.assertEqual(linter.config.ignore_bad_template, True)
    #    self.assertEqual(linter.config.ignore_checks, [])
    #    self.assertEqual(linter.config.include_checks, ['E', 'W', ])
    #    self.assertEqual(linter.config.listrules, False)
    #    self.assertEqual(linter.config.debug, False)
    #    self.assertEqual(linter.config.override_spec, None)
    #    self.assertEqual(linter.config.regions, ['us-east-1'])
    #    self.assertEqual(linter.config.templates, [filename])
    #    self.assertEqual(linter.config.update_documentation, False)
    #    self.assertEqual(linter.config.update_specs, False)

    @patch('sys.stdout')
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli(self, yaml_mock, _):
        """ Test run CLI and exit code"""
        yaml_mock.side_effect = [
            {},
            {}
        ]

        setattr(self.linter.config.cli_args, 'listrules', True)
        self.assertEqual(0, self.linter.run_cli())

    @patch('cfnlint.maintenance.update_resource_specs', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli_update_specs(self, yaml_mock, _):
        """ Test run CLI and update specs"""
        yaml_mock.side_effect = [
            {},
            {}
        ]

        setattr(self.linter.config.cli_args, 'update_specs', True)
        self.assertEqual(0, self.linter.run_cli())

    @patch('cfnlint.maintenance.update_documentation', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli_update_documentation(self, yaml_mock, _):
        """ Test run CLI and update specs"""
        yaml_mock.side_effect = [
            {},
            {}
        ]
        setattr(self.linter.config.cli_args, 'update_documentation', True)
        self.assertEqual(0, self.linter.run_cli())

    @patch('cfnlint.maintenance.update_iam_policies', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli_update_iam_policies(self, yaml_mock, _):
        """ Test run CLI and update iam policies"""
        yaml_mock.side_effect = [
            {},
            {}
        ]

        setattr(self.linter.config.cli_args, 'update_iam_policies', True)
        self.assertEqual(0, self.linter.run_cli())

    @patch('cfnlint.Linter.lint', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli_lint_success(self, yaml_mock, lint_mock):
        """ Test run CLI and actually lint """

        yaml_mock.side_effect = [
            {},
            {}
        ]

        self.linter.config.templates = [self.filename]

        def mocklinter():
            self.linter.matches = []

        lint_mock.side_effect = mocklinter

        # success test
        self.assertEqual(0, self.linter.run_cli())

    @patch('cfnlint.sys.stdout')
    @patch('cfnlint.Linter.lint', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli_lint_error(self, yaml_mock, lint_mock, stdout_mock):
        """ Test run CLI and actually lint """

        yaml_mock.side_effect = [
            {},
            {}
        ]

        self.linter.config.templates = [self.filename]

        def mocklinter():
            self.linter.matches = [self.match_error, self.match_warning, self.match_info]

        lint_mock.side_effect = mocklinter

        # error test
        self.assertEqual(14, self.linter.run_cli())
        stdout_mock.write.assert_has_calls([
            mock.call(
                'E0000 error\ntest.yaml:1:1\n\nW0000 warning\ntest.yaml:1:1\n\nI0000 warning\ntest.yaml:1:1\n'),
            mock.call('\n'),
        ])

    @patch('cfnlint.Linter.lint', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli_with_stdin(self, yaml_mock, lint_mock):
        """Test getting the template from stdin doesn't crash"""

        yaml_mock.side_effect = [
            {},
            {}
        ]

        lint_mock.side_effect = [
            [],
        ]

        filename = 'test/fixtures/templates/good/generic.yaml'
        with open(filename, 'r') as fp:
            file_content = fp.read()

        with patch('sys.stdin', StringIO(file_content)):
            linter = cfnlint.CliLinter([])
            matches = linter.run_cli()
            self.assertEqual(0, matches)

    @patch('argparse.ArgumentParser.print_help', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_run_cli_with_no_template(self, yaml_mock, help_mock):
        """Test no parameters returns 1"""

        yaml_mock.side_effect = [
            {},
            {}
        ]

        return_value = self.linter.run_cli()
        self.assertEqual(1, return_value)
        self.assertTrue(help_mock.called)

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_exit_codes(self, yaml_mock):
        """ Test run CLI and actually lint """

        yaml_mock.side_effect = [
            {},
            {}
        ]

        self.linter.config.templates = [self.filename]

        self.linter.matches = []
        self.assertEqual(0, self.linter.get_exit_code())

        self.linter.matches = [self.match_error]
        self.assertEqual(2, self.linter.get_exit_code())

        self.linter.matches = [self.match_warning]
        self.assertEqual(4, self.linter.get_exit_code())

        self.linter.matches = [self.match_info]
        self.assertEqual(8, self.linter.get_exit_code())

        self.linter.matches = [self.match_error, self.match_warning, self.match_info]
        self.assertEqual(14, self.linter.get_exit_code())

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_get_formatter_json(self, yaml_mock):
        """ Test run CLI and get formatters """

        yaml_mock.side_effect = [
            {},
            {}
        ]

        self.linter.config._manual_args['format'] = 'json'
        self.assertIsInstance(self.linter._get_formatter(), (cfnlint.formatters.JsonFormatter))

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_get_formatter_quiet(self, yaml_mock):
        """ Test run CLI and get formatters """

        yaml_mock.side_effect = [
            {},
            {}
        ]

        self.linter.config._manual_args['format'] = 'quiet'
        self.assertIsInstance(self.linter._get_formatter(), (cfnlint.formatters.QuietFormatter))

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_get_formatter_parseable(self, yaml_mock):
        """ Test run CLI and get formatters """

        yaml_mock.side_effect = [
            {},
            {}
        ]

        self.linter.config._manual_args['format'] = 'parseable'
        self.assertIsInstance(self.linter._get_formatter(), (cfnlint.formatters.ParseableFormatter))

    @patch('cfnlint.config.ConfigMixIn', create=True)
    def test_get_config_failure(self, config_mock):
        """ Test run CLI and get formatters """

        config_mock.side_effect = jsonschema.exceptions.ValidationError('fail')
        with self.assertRaises(cfnlint.InvalidConfiguation):
            cfnlint.CliLinter([])
