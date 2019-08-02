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
            'filename': 'test/fixtures/templates/public/lambda-poller.yaml',
            'results_filename': 'test/fixtures/results/public/lambda-poller.json',
            'exit_code': 2,
        },
        {
            'filename': 'test/fixtures/templates/public/watchmaker.json',
            'results_filename': 'test/fixtures/results/public/watchmaker.json',
            'exit_code': 8,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_high_master.yaml',
            'results_filename': 'test/fixtures/results/quickstart/nist_high_master.json',
            'exit_code': 14,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_application.yaml',
            'results_filename': 'test/fixtures/results/quickstart/nist_application.json',
            'exit_code': 14,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_config_rules.yaml',
            'results_filename': 'test/fixtures/results/quickstart/nist_config_rules.json',
            'exit_code': 6,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_iam.yaml',
            'results_filename': 'test/fixtures/results/quickstart/nist_iam.json',
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_logging.yaml',
            'results_filename': 'test/fixtures/results/quickstart/nist_logging.json',
            'exit_code': 14,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_vpc_management.yaml',
            'results_filename': 'test/fixtures/results/quickstart/nist_vpc_management.json',
            'exit_code': 14,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/nist_vpc_production.yaml',
            'results_filename': 'test/fixtures/results/quickstart/nist_vpc_production.json',
            'exit_code': 14,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/openshift_master.yaml',
            'results_filename': 'test/fixtures/results/quickstart/openshift_master.json',
            'exit_code': 8,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/openshift.yaml',
            'results_filename': 'test/fixtures/results/quickstart/openshift.json',
            'exit_code': 14,
        },
        {
            'filename': 'test/fixtures/templates/quickstart/cis_benchmark.yaml',
            'results_filename': 'test/fixtures/results/quickstart/cis_benchmark.json',
            'exit_code': 6,
        }
    ]

    def test_templates(self):
        """Test Successful JSON Parsing"""
        self.maxDiff = None
        self.run_scenarios([
            '--include-checks', 'I',
            '--include-expiremental',
        ])

    def test_module_integration_legacy(self):
        """ Test same templates using integration approach"""

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            rules = cfnlint.core.get_rules(
                [], [], ['I', 'E', 'W'], {}, True)
            self.run_module_legacy_integration_scenarios(rules)
