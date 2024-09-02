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
            "results_filename": "test/fixtures/results/public/lambda-poller.json",
            "exit_code": 2,
        },
        {
            "filename": "test/fixtures/templates/public/watchmaker.json",
            "results_filename": "test/fixtures/results/public/watchmaker.json",
            "exit_code": 8,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_high_main.yaml",
            "results_filename": "test/fixtures/results/quickstart/nist_high_main.json",
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_application.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart" "/nist_application.json"
            ),
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_config_rules.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/" "nist_config_rules.json"
            ),
            "exit_code": 6,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_iam.yaml",
            "results_filename": "test/fixtures/results/quickstart/nist_iam.json",
            "exit_code": 4,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_logging.yaml",
            "results_filename": "test/fixtures/results/quickstart/nist_logging.json",
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_vpc_management.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/" "nist_vpc_management.json"
            ),
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/nist_vpc_production.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart/" "nist_vpc_production.json"
            ),
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/openshift_master.yaml",
            "results_filename": (
                "test/fixtures/results/quickstart" "/openshift_master.json"
            ),
            "exit_code": 8,
        },
        {
            "filename": "test/fixtures/templates/quickstart/openshift.yaml",
            "results_filename": "test/fixtures/results/quickstart/openshift.json",
            "exit_code": 14,
        },
        {
            "filename": "test/fixtures/templates/quickstart/cis_benchmark.yaml",
            "results_filename": "test/fixtures/results/quickstart/cis_benchmark.json",
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
