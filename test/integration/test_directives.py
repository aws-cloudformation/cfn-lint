"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path
from test.integration import BaseCliTestCase


class TestDirectives(BaseCliTestCase):
    """Test Directives"""

    # ruff: noqa: E501
    scenarios = [
        {
            "filename": str(Path("test/fixtures/templates/good/core/directives.yaml")),
            "exit_code": 4,
            "results_filename": "test/fixtures/results/good/core/directives_yaml.json",
        },
        {
            "filename": str(Path("test/fixtures/templates/bad/core/directives.yaml")),
            "exit_code": 6,
            "results_filename": "test/fixtures/results/bad/core/directives_yaml.json",
        },
    ]

    def test_templates(self):
        """Test ignoring certain rules"""
        self.run_scenarios()
