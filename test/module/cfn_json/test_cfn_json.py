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
import sys
from mock import patch
from six import StringIO
from cfnlint import Template, RulesCollection  # pylint: disable=E0401
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_json  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestCfnJson(BaseTestCase):
    """Test JSON Parsing """
    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection(include_experimental=True)
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

        self.filenames = {
            "config_rule": {
                "filename": 'test/fixtures/templates/quickstart/config-rules.json',
                "failures": 6
            },
            "iam": {
                "filename": 'test/fixtures/templates/quickstart/iam.json',
                "failures": 5
            },
            "nat_instance": {
                "filename": 'test/fixtures/templates/quickstart/nat-instance.json',
                "failures": 2
            },
            "vpc_management": {
                "filename": 'test/fixtures/templates/quickstart/vpc-management.json',
                "failures": 35
            },
            "vpc": {
                "filename": 'test/fixtures/templates/quickstart/vpc.json',
                "failures": 40
            },
            "poller": {
                "filename": 'test/fixtures/templates/public/lambda-poller.json',
                "failures": 1
            }
        }

    def test_success_parse(self):
        """Test Successful JSON Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')

            template = cfnlint.decode.cfn_json.load(filename)
            cfn = Template(filename, template, ['us-east-1'])

            matches = []
            matches.extend(self.rules.run(filename, cfn))
            assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(failures, len(matches), filename)

    def test_success_escape_character(self):
        """Test Successful JSON Parsing"""
        failures = 1
        filename = 'test/fixtures/templates/good/decode/parsing.json'
        template = cfnlint.decode.cfn_json.load(filename)
        cfn = Template(filename, template, ['us-east-1'])

        matches = []
        matches.extend(self.rules.run(filename, cfn))
        assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(failures, len(matches), filename)

    def test_success_parse_stdin(self):
        """Test Successful JSON Parsing through stdin"""
        for _, values in self.filenames.items():
            filename = '-'
            failures = values.get('failures')
            with open(values.get('filename'), 'r') as fp:
                file_content = fp.read()
            with patch('sys.stdin', StringIO(file_content)):

                template = cfnlint.decode.cfn_json.load(filename)
                cfn = Template(filename, template, ['us-east-1'])

                matches = []
                matches.extend(self.rules.run(filename, cfn))
                assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(failures, len(matches), values.get('filename'))

    def test_fail_run(self):
        """Test failure run"""

        filename = 'test/fixtures/templates/bad/json_parse.json'

        try:
            template = cfnlint.decode.cfn_json.load(filename)
        except cfnlint.decode.cfn_json.JSONDecodeError:
            assert(True)
            return

        assert(False)
