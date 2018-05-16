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
import cfnlint.helpers  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestDefaultArguments(BaseTestCase):
    """Test Default Arguments """

    def test_default_arguments(self):
        """Test success run"""

        filename = 'templates/good/helpers/config_cfn_lint.yaml'
        ignore_bad_template = True

        (defaults, _) = cfnlint.helpers.get_template_default_args(filename, ignore_bad_template)

        assert(defaults == {'regions': ['us-east-1', 'us-east-2'], 'ignore_checks': ['E2530']})

    def test_template_not_found(self):
        """Test template not found"""
        filename = 'templates/good/helpers/not_found.yaml'
        ignore_bad_template = True

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.helpers.get_template_default_args(filename, ignore_bad_template)

        self.assertEqual(exit_code.exception.code, 1)

    def test_template_invalid_yaml(self):
        """Test template not found"""
        filename = 'templates/bad/helpers/config_invalid_yaml.yaml'
        ignore_bad_template = False

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.helpers.get_template_default_args(filename, ignore_bad_template)

        self.assertEqual(exit_code.exception.code, 1)

    def test_template_invalid_json(self):
        """Test template not found"""
        filename = 'templates/bad/helpers/config_invalid_json.json'
        ignore_bad_template = False

        with self.assertRaises(SystemExit) as exit_code:
            cfnlint.helpers.get_template_default_args(filename, ignore_bad_template)

        self.assertEqual(exit_code.exception.code, 1)

    def test_template_invalid_yaml_ignore(self):
        """Test template not found"""
        filename = 'templates/bad/helpers/config_invalid_yaml.yaml'
        ignore_bad_template = True

        (defaults, _) = cfnlint.helpers.get_template_default_args(filename, ignore_bad_template)

        self.assertEqual(defaults, {})

    def test_template_invalid_json_ignore(self):
        """Test template not found"""
        filename = 'templates/bad/helpers/config_invalid_json.json'
        ignore_bad_template = True

        (defaults, _) = cfnlint.helpers.get_template_default_args(filename, ignore_bad_template)

        self.assertEqual(defaults, {})
