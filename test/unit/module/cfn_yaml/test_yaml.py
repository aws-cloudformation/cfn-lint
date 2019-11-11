"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from six import StringIO
from mock import patch
from cfnlint import Template  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401


class TestYamlParse(BaseTestCase):
    """Test YAML Parsing """

    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

        self.filenames = {
            "config_rule": {
                "filename": 'test/fixtures/templates/public/lambda-poller.yaml',
                "failures": 1
            },
            "generic_bad": {
                "filename": 'test/fixtures/templates/bad/generic.yaml',
                "failures": 35
            }
        }

    def test_success_parse(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])

            matches = []
            matches.extend(self.rules.run(filename, cfn))
            assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(
                failures, len(matches), filename)

    def test_success_parse_stdin(self):
        """Test Successful YAML Parsing through stdin"""
        for _, values in self.filenames.items():
            filename = '-'
            failures = values.get('failures')
            with open(values.get('filename'), 'r') as fp:
                file_content = fp.read()

            with patch('sys.stdin', StringIO(file_content)):
                template = cfnlint.decode.cfn_yaml.load(filename)
                cfn = Template(filename, template, ['us-east-1'])

                matches = []
                matches.extend(self.rules.run(filename, cfn))
                assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(
                    failures, len(matches), values.get('filename'))
