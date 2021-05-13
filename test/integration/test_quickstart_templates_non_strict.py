"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.integration import BaseCliTestCase
import cfnlint.core


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing """

    scenarios = [
        {
            'filename': 'test/fixtures/templates/quickstart/nist_high_main.yaml',
            'results_filename': 'test/fixtures/results/quickstart/non_strict/nist_high_main.json',
            'exit_code': 14,
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

    def test_module_integration(self):
        """ Test same templates using integration approach"""
        rules = cfnlint.core.get_rules(
            [], [], ['I', 'E', 'W'],
            {
                'E3012': {
                    'strict': False,
                }
            }, True)
        self.run_module_integration_scenarios(rules)
