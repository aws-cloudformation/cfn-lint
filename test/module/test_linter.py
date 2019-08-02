"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import jsonschema
from jsonschema.exceptions import ValidationError
from mock import patch
import cfnlint.helpers
from testlib.testcase import BaseTestCase


class TestLinter(BaseTestCase):
    """Test Template Class in cfnlint """

    def test_lint(self):
        """Test success run"""

        linter = cfnlint.Linter()
        linter.config.templates = ['test/fixtures/templates/good/generic.yaml']
        linter.lint()

        self.assertEqual(linter.matches, [])

    def test_lint_bad_template(self):
        """Test bad template"""

        linter = cfnlint.Linter()
        linter.config.templates = ['test/fixtures/templates/bad/duplicate.yaml']
        linter.lint()

        self.assertEqual(linter.matches, [
            cfnlint.rules.Match(
                linenumber=9,
                columnnumber=3,
                linenumberend=9,
                columnnumberend=13,
                filename='test/fixtures/templates/bad/duplicate.yaml',
                message='Duplicate resource found "mySnsTopic" (line 9)',
                rule=cfnlint.rules.ParseError()
            )
        ])

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_lint_bad_config(self, yaml_mock):
        """ Test when there is a bad config file that isn't parseable """

        yaml_mock.side_effect = [
            {"regions": True}, {}
        ]

        with self.assertRaises(cfnlint.InvalidConfiguation):
            cfnlint.Linter()
