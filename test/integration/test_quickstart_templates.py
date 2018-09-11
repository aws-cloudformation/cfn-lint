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
from cfnlint import Template, RulesCollection, Runner  # pylint: disable=E0401
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestQuickStartTemplates(BaseTestCase):
    """Test QuickStart Templates Parsing """
    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.extend(
                RulesCollection.create_from_directory(rulesdir))

        self.filenames = {
            'config_rule': {
                "filename": 'fixtures/templates/public/lambda-poller.yaml',
                "failures": 0
            },
            'watchmaker': {
                "filename": 'fixtures/templates/public/watchmaker.json',
                "failures": 0
            },
            'nist_high_master': {
                'filename': 'fixtures/templates/quickstart/nist_high_master.yaml',
                'results_filename': 'fixtures/results/quickstart/nist_high_master.json'
            },
            'nist_application': {
                'filename': 'fixtures/templates/quickstart/nist_application.yaml',
                'results_filename': 'fixtures/results/quickstart/nist_application.json'
            },
            'nist_config_rules': {
                'filename': 'fixtures/templates/quickstart/nist_config_rules.yaml',
                'results_filename': 'fixtures/results/quickstart/nist_config_rules.json'
            },
            'nist_iam': {
                'filename': 'fixtures/templates/quickstart/nist_iam.yaml',
                'results_filename': 'fixtures/results/quickstart/nist_iam.json'
            },
            'nist_logging': {
                'filename': 'fixtures/templates/quickstart/nist_logging.yaml',
                'results_filename': 'fixtures/results/quickstart/nist_logging.json'
            },
            'nist_vpc_management': {
                'filename': 'fixtures/templates/quickstart/nist_vpc_management.yaml',
                'results_filename': 'fixtures/results/quickstart/nist_vpc_management.json'
            },
            'nist_vpc_production': {
                'filename': 'fixtures/templates/quickstart/nist_vpc_production.yaml',
                'results_filename': 'fixtures/results/quickstart/nist_vpc_production.json'
            },
            'openshift_master': {
                'filename': 'fixtures/templates/quickstart/openshift_master.yaml',
                'failures': 0
            },
            'openshift': {
                'filename': 'fixtures/templates/quickstart/openshift.yaml',
                'results_filename': 'fixtures/results/quickstart/openshift.json'
            },
            'cis_benchmark': {
                'filename': 'fixtures/templates/quickstart/cis_benchmark.yaml',
                'results_filename': 'fixtures/results/quickstart/cis_benchmark.json'
            }
        }

    def test_templates(self):
        """Test Successful JSON Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            results_filename = values.get('results_filename')
            template = cfnlint.decode.cfn_yaml.load(filename)

            runner = Runner(self.rules, filename, template, ['us-east-1'])
            matches = []
            matches.extend(runner.transform())
            if not matches:
                matches.extend(runner.run())

            if results_filename:
                with open(results_filename) as json_data:
                    correct = json.load(json_data)

                assert len(matches) == len(correct), 'Expected {} failures, got {} on {}'.format(len(correct), len(matches), filename)
                for c in correct:
                    matched = False
                    for match in matches:
                        if c['Location']['Start']['LineNumber'] == match.linenumber and \
                                c['Location']['Start']['ColumnNumber'] == match.columnnumber and \
                                c['Rule']['Id'] == match.rule.id:
                            matched = True
                    assert matched is True, 'Expected error {} at line {}, column {} in matches for {}'.format(c['Rule']['Id'], c['Location']['Start']['LineNumber'], c['Location']['Start']['ColumnNumber'], filename)
            else:
                assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(failures, len(matches), filename)
