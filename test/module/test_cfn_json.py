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
from cfnlint import Template, RulesCollection, DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.cfn_json  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestCfnJson(BaseTestCase):
    """Test JSON Parsing """
    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.extend(
                RulesCollection.create_from_directory(rulesdir))

        self.filenames = {
            "config_rule": {
                "filename": 'templates/quickstart/config-rules.json',
                "failures": 0
            },
            "iam": {
                "filename": 'templates/quickstart/iam.json',
                "failures": 0
            },
            "nat_instance": {
                "filename": 'templates/quickstart/nat-instance.json',
                "failures": 2
            },
            "vpc_management": {
                "filename": 'templates/quickstart/vpc-management.json',
                "failures": 14
            },
            "vpc": {
                "filename": 'templates/quickstart/vpc.json',
                "failures": 0
            }
        }

    def test_success_parse(self):
        """Test Successful JSON Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = json.load(open(filename), cls=cfnlint.cfn_json.CfnJSONDecoder)
            cfn = Template(template, ['us-east-1'])

            matches = list()
            matches.extend(self.rules.run(filename, cfn, []))
            assert(len(matches) == failures)

    def test_fail_run(self):
        """Test failure run"""

        filename = 'templates/bad/json_parse.json'

        try:
            json.load(open(filename), cls=cfnlint.cfn_json.CfnJSONDecoder)
        except cfnlint.cfn_json.JSONDecodeError:
            assert(True)
            return

        assert(False)
