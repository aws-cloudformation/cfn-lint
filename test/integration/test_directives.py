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
from cfnlint import Template, Runner  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestDirectives(BaseTestCase):
    """Test Directives """

    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection(include_rules=['I'])
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

    def test_templates(self):
        """Test ignoring certain rules"""
        filename = 'test/fixtures/templates/bad/core/directives.yaml'
        failures = 5

        template = cfnlint.decode.cfn_yaml.load(filename)
        runner = Runner(self.rules, filename, template, ['us-east-1'])
        matches = []
        matches.extend(runner.transform())
        if not matches:
            matches.extend(runner.run())
        assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(
            failures, len(matches), filename)
