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
from cfnlint import Runner, RulesCollection, DEFAULT_RULESDIR
import cfnlint.helpers  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestDefaultArguments(BaseTestCase):
    """Test Run Checks """
    def setUp(self):
        """Setup"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.extend(
                RulesCollection.create_from_directory(rulesdir))

    def test_good_template(self):
        """Test success run"""

        filename = 'templates/good/generic.yaml'
        (_, template) = cfnlint.helpers.get_template_default_args(filename, True)

        results = cfnlint.helpers.run_checks(
            filename, template, self.rules, {}, {}, ['us-east-1'])

        assert(results == [])

    def test_bad_template(self):
        """Test bad template"""

        filename = 'templates/quickstart/nat-instance.json'
        (_, template) = cfnlint.helpers.get_template_default_args(filename, True)

        results = cfnlint.helpers.run_checks(
            filename, template, self.rules, {}, {}, ['us-east-1'])

        assert(results[0].rule.id == 'W2506')
        assert(results[1].rule.id == 'W2001')
