"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.integration import BaseCliTestCase

import cfnlint.core


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
        rules = cfnlint.core.get_rules(
            [], [], ["I", "E", "W"], {"E3012": {"strict": True}}, True
        )
        self.run_module_integration_scenarios(rules)
