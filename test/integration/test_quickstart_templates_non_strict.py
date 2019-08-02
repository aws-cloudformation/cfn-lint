"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import warnings
from test.integration import BaseCliTestCase
import cfnlint.core


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing """

    scenarios = [
        {
            'filename': 'test/fixtures/templates/quickstart/nist_high_master.yaml',
            'results_filename': 'test/fixtures/results/quickstart/non_strict/nist_high_master.json',
            'exit_code': 12,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_application.yaml',
            'results_filename': 'test/fixtures/results/quickstart/non_strict/nist_application.json',
            'exit_code': 12,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/openshift.yaml',
            'results_filename': 'test/fixtures/results/quickstart/non_strict/openshift.json',
            'exit_code': 12,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/cis_benchmark.yaml',
            'results_filename': 'test/fixtures/results/quickstart/non_strict/cis_benchmark.json',
            'exit_code': 4,
        }
    ]

    def test_templates(self):
        """Test Successful JSON Parsing"""
        self.maxDiff = None
        self.run_scenarios([
            '--include-checks', 'I',
            '--include-expiremental',
            '--configure-rule', 'E3012:strict=false',
        ])

    def test_module_integration_legacy(self):
        """ Test same templates using integration approach"""

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            rules = cfnlint.core.get_rules(
                [], [], ['I', 'E', 'W'],
                {
                    'E3012': {
                        'strict': False,
                    }
                }, True)
            self.run_module_legacy_integration_scenarios(rules)
