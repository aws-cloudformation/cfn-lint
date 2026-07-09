"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.integration import BaseCliTestCase

from cfnlint import ConfigMixIn


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing"""

    scenarios = [
        {
            "filename": "test/fixtures/templates/public/lambda-poller.yaml",
            "results_filename": "test/fixtures/results/public/lambda-poller_yaml.json",
            "exit_code": 2,
        },
        {
            "filename": "test/fixtures/templates/public/watchmaker.json",
            "results_filename": "test/fixtures/results/public/watchmaker_json.json",
            "exit_code": 8,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_high_main.yaml",
            "results_filename": "test/fixtures/results/quickstart/nist_high_main_yaml.json",
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_application.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/nist_application_yaml.json"
            ),
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_config_rules.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/nist_config_rules_yaml.json"
            ),
            "exit_code": 6,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_iam.yaml",
            "results_filename": "test/fixtures/results/quickstart/nist_iam_yaml.json",
            "exit_code": 4,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_logging.yaml",
            "results_filename": "test/fixtures/results/quickstart/nist_logging_yaml.json",
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_vpc_management.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/nist_vpc_management_yaml.json"
            ),
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_vpc_production.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/nist_vpc_production_yaml.json"
            ),
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/openshift_master.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/openshift_master_yaml.json"
            ),
            "exit_code": 8,
        },
        {
            "filename": "test/fixtures/templates/quickstart/openshift.yaml",
            "results_filename": "test/fixtures/results/quickstart/openshift_yaml.json",
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/cis_benchmark.yaml",
            "results_filename": "test/fixtures/results/quickstart/cis_benchmark_yaml.json",
            "exit_code": 6,
        },
    ]

    def test_templates(self):
        """Test same templates using integration approach"""
        self.run_module_integration_scenarios(
            ConfigMixIn(
                [],
                include_checks=["I"],
                configure_rules={"E3012": {"strict": True}},
                include_experimental=True,
            )
        )
