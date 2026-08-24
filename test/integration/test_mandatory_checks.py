"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path
from test.integration import BaseCliTestCase
from typing import Any, Dict, List


class TestDirectives(BaseCliTestCase):
    """Test Directives"""

    # ruff: noqa: E501
    scenarios: List[Dict[str, Any]] = [
        {
            "filename": str(
                Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
            ),
            "exit_code": 6,
            "results_filename": "test/fixtures/results/bad/core/mandatory_checks_yaml.json",
        }
    ]

    def test_templates_explicit(self):
        """Test making certain rules mandatory explictly"""
        self.run_scenarios(["--mandatory-checks", "E3001", "E3002"])

    def test_templates_prefixed(self):
        """Test making certain rules mandatory via a rule prefix"""
        self.run_scenarios(["--mandatory-checks", "E300"])
