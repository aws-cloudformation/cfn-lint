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
import json
from cfnlint import Template, RulesCollection
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
import cfnlint.decode.cfn_json  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestDuplicate(BaseTestCase):
    """Test Duplicates Parsing """
    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.extend(
                RulesCollection.create_from_directory(rulesdir))

    def test_success_run(self):
        """Test success run"""

        filename = 'fixtures/templates/good/generic.yaml'

        try:
            cfnlint.decode.cfn_yaml.load(filename)
        except cfnlint.decode.cfn_yaml.CfnParseError:
            assert(False)
            return

        assert(True)

    def test_fail_json_run(self):
        """Test failure run"""

    def test_fail_run(self):
        """Test failure run"""

        filename = 'fixtures/templates/bad/duplicate.json'

        try:
            with open(filename) as fp:
                json.load(fp, cls=cfnlint.decode.cfn_json.CfnJSONDecoder)
        except cfnlint.decode.cfn_json.JSONDecodeError:
            assert(True)
            return

        assert(False)

    def test_fail_yaml_run(self):
        """Test failure run"""

        filename = 'fixtures/templates/bad/duplicate.yaml'

        try:
            cfnlint.decode.cfn_yaml.load(filename)
        except cfnlint.decode.cfn_yaml.CfnParseError:
            assert(True)
            return

        assert(False)
