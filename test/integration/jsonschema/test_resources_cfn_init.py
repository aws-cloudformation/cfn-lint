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
            "filename": (
                "test/fixtures/templates/integration/good"
                "/resources-cloudformation-init.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/integration/"
                "good/resources-cloudformation-init.json"
            ),
            "exit_code": 0,
        },
    ]

    def test_templates(self):
        """Test same templates using integration approach"""
        self.run_module_integration_scenarios(
            ConfigMixIn(
                [],
                include_checks=["I"],
                configure_rules={
                    "E3012": {
                        "strict": True,
                    }
                },
                include_experimental=True,
            )
        )
