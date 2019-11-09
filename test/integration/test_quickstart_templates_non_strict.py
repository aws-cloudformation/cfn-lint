"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from cfnlint import Runner  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestQuickStartTemplatesNonStrict(BaseTestCase):
    """Test QuickStart Templates Parsing """

    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection(
            include_rules=['I'],
            include_experimental=True,
            configure_rules={'E3012': {'strict': 'false'}}
        )
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

        self.filenames = {
            'nist_high_master': {
                'filename': 'test/fixtures/templates/quickstart/nist_high_master.yaml',
                'results_filename': 'test/fixtures/results/quickstart/non_strict/nist_high_master.json'
            },
            'nist_application': {
                'filename': 'test/fixtures/templates/quickstart/nist_application.yaml',
                'results_filename': 'test/fixtures/results/quickstart/non_strict/nist_application.json'
            },
            'openshift': {
                'filename': 'test/fixtures/templates/quickstart/openshift.yaml',
                'results_filename': 'test/fixtures/results/quickstart/non_strict/openshift.json'
            },
            'cis_benchmark': {
                'filename': 'test/fixtures/templates/quickstart/cis_benchmark.yaml',
                'results_filename': 'test/fixtures/results/quickstart/non_strict/cis_benchmark.json'
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

                assert len(matches) == len(correct), 'Expected {} failures, got {} on {}'.format(
                    len(correct), len(matches), filename)
                for c in correct:
                    matched = False
                    for match in matches:
                        if c['Location']['Start']['LineNumber'] == match.linenumber and \
                                c['Location']['Start']['ColumnNumber'] == match.columnnumber and \
                                c['Rule']['Id'] == match.rule.id:
                            matched = True
                    assert matched is True, 'Expected error {} at line {}, column {} in matches for {}'.format(
                        c['Rule']['Id'], c['Location']['Start']['LineNumber'], c['Location']['Start']['ColumnNumber'], filename)
            else:
                assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(
                    failures, len(matches), filename)
