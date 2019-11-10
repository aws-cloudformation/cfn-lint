"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from test.testlib.testcase import BaseTestCase
import cfnlint.config  # pylint: disable=E0401

LOGGER = logging.getLogger('cfnlint')


class TestArgsParser(BaseTestCase):
    """Test Parser Arguments """

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_create_parser(self):
        """Test success run"""

        config = cfnlint.config.CliArgs([
            '-t', 'test.yaml', '--ignore-bad-template',
            '--format', 'quiet', '--debug'])
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(config.cli_args.template_alt, ['test.yaml'])
        self.assertEqual(config.cli_args.ignore_bad_template, True)
        self.assertEqual(config.cli_args.format, 'quiet')
        self.assertEqual(config.cli_args.debug, True)

    def test_create_parser_default_param(self):
        """Test success run"""

        config = cfnlint.config.CliArgs([
            '--regions', 'us-east-1', 'us-west-2', '--', 'template1.yaml', 'template2.yaml'])
        self.assertEqual(config.cli_args.templates, ['template1.yaml', 'template2.yaml'])
        self.assertEqual(config.cli_args.template_alt, [])
        self.assertEqual(config.cli_args.regions, ['us-east-1', 'us-west-2'])

    def test_create_parser_exend(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(['-t', 'template1.yaml', '-t', 'template2.yaml'])
        self.assertEqual(config.cli_args.templates, [])
        self.assertEqual(config.cli_args.template_alt, ['template1.yaml', 'template2.yaml'])

    def test_create_parser_config_file(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            ['--regions', 'us-west-1', '--include-checks', 'I1234', '--', 'template1.yaml'])
        self.assertEqual(config.cli_args.templates, ['template1.yaml'])
        self.assertEqual(config.cli_args.include_checks, ['I1234'])
        self.assertEqual(config.cli_args.regions, ['us-west-1'])

    def test_create_parser_rule_configuration(self):
        """Test success run"""

        config = cfnlint.config.CliArgs(
            ['-x', 'E3012:strict=true', '-x', 'E3012:key=value,E3001:key=value'])
        self.assertEqual(config.cli_args.configure_rules, {
                         'E3012': {'key': 'value', 'strict': 'true'}, 'E3001': {'key': 'value'}})
