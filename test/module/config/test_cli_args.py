"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import logging
from mock import patch, mock_open
import cfnlint.config  # pylint: disable=E0401
from testlib.testcase import BaseTestCase

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

        config = cfnlint.config.CliArgs(['--regions', 'us-west-1', '--include-checks', 'I1234', '--', 'template1.yaml'])
        self.assertEqual(config.cli_args.templates, ['template1.yaml'])
        self.assertEqual(config.cli_args.include_checks, ['I1234'])
        self.assertEqual(config.cli_args.regions, ['us-west-1'])
