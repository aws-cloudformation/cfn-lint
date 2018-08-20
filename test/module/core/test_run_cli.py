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
import cfnlint.core  # pylint: disable=E0401
from testlib.testcase import BaseTestCase

LOGGER = logging.getLogger('cfnlint')


class TestCli(BaseTestCase):
    """Test CLI processing """
    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_template_not_found(self):
        """Test template not found"""

        filename = 'fixtures/templates/good/core/not_found.yaml'

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.core.get_template_args_rules([
                '--template', filename, '--ignore_bad_template'])

        self.assertEqual(exit_code.exception.code, 1)

    def test_template_invalid_yaml(self):
        """Test template not found"""
        filename = 'fixtures/templates/bad/core/config_invalid_yaml.yaml'

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.core.get_template_args_rules([
                '--template', filename])

        self.assertEqual(exit_code.exception.code, 2)

    def test_template_invalid_json(self):
        """Test template not found"""
        filename = 'fixtures/templates/bad/core/config_invalid_json.json'

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.core.get_template_args_rules([
                '--template', filename])

        self.assertEqual(exit_code.exception.code, 2)

    def test_template_invalid_yaml_ignore(self):
        """Test template not found"""
        filename = 'fixtures/templates/bad/core/config_invalid_yaml.yaml'

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.core.get_template_args_rules([
                '--template', filename, '--ignore-bad-template'])

        self.assertEqual(exit_code.exception.code, 2)

    def test_template_invalid_json_ignore(self):
        """Test template not found"""
        filename = 'fixtures/templates/bad/core/config_invalid_json.json'

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.core.get_template_args_rules([
                '--template', filename, '--ignore-bad-template'])

        self.assertEqual(exit_code.exception.code, 2)

    def test_template_config(self):
        """Test template config"""
        filename = 'fixtures/templates/good/core/config_parameters.yaml'
        (args, _, _, _, _) = cfnlint.core.get_template_args_rules([
            '--template', filename, '--ignore-bad-template'])

        self.assertEqual(vars(args), {
            'append_rules': [],
            'format': None,
            'ignore_bad_template': True,
            'ignore_checks': ['E0101'],
            'listrules': False,
            'debug': False,
            'override_spec': None,
            'regions': ['us-east-1'],
            'template_alt': 'fixtures/templates/good/core/config_parameters.yaml',
            'template': None,
            'update_documentation': False,
            'update_specs': False})

    def test_positional_template_parameters(self):
        """Test overriding parameters"""
        filename = 'fixtures/templates/good/core/config_parameters.yaml'
        (args, _, _, _, _) = cfnlint.core.get_template_args_rules([
            filename, '--ignore-bad-template',
            '--ignore-checks', 'E0000'])

        self.assertEqual(vars(args), {
            'append_rules': [],
            'format': None,
            'ignore_bad_template': True,
            'ignore_checks': ['E0000'],
            'listrules': False,
            'debug': False,
            'override_spec': None,
            'regions': ['us-east-1'],
            'template_alt': None,
            'template': 'fixtures/templates/good/core/config_parameters.yaml',
            'update_documentation': False,
            'update_specs': False})

    def test_override_parameters(self):
        """Test overriding parameters"""
        filename = 'fixtures/templates/good/core/config_parameters.yaml'
        (args, _, _, _, _) = cfnlint.core.get_template_args_rules([
            '--template', filename, '--ignore-bad-template',
            '--ignore-checks', 'E0000'])

        self.assertEqual(vars(args), {
            'append_rules': [],
            'format': None,
            'ignore_bad_template': True,
            'ignore_checks': ['E0000'],
            'listrules': False,
            'debug': False,
            'override_spec': None,
            'regions': ['us-east-1'],
            'template_alt': 'fixtures/templates/good/core/config_parameters.yaml',
            'template': None,
            'update_documentation': False,
            'update_specs': False})

    def test_bad_config(self):
        """ Test bad formatting in config"""

        filename = 'fixtures/templates/bad/core/config_parameters.yaml'
        (args, _, _, _, _) = cfnlint.core.get_template_args_rules([
            '--template', filename, '--ignore-bad-template'])

        self.assertEqual(vars(args), {
            'append_rules': [],
            'format': None,
            'ignore_bad_template': True,
            'ignore_checks': [],
            'listrules': False,
            'debug': False,
            'override_spec': None,
            'regions': ['us-east-1'],
            'template_alt': filename,
            'template': None,
            'update_documentation': False,
            'update_specs': False})
