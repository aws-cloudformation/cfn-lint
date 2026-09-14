"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.integration import BaseCliTestCase

from cfnlint import ConfigMixIn


class TestTransformIgnore(BaseCliTestCase):
    """Test Ignoring Transform Failure"""

    scenarios = [
        {
            "filename": (
                "test/fixtures/templates/bad/transform_serverless_template.yaml"
            ),
            # SAM transform errors (E0001) no longer occur since SAM resources
            # are validated directly via schemas. The template still has schema
            # errors (E3003, E3012, etc.) which produce exit code 10 (error +
            # informational).
            "results_filename": (
                "test/fixtures/results/transform_ignore"
                "/transform_serverless_template.json"
            ),
            "exit_code": 10,
        },
    ]

    def test_templates(self):
        """Test same templates using integration approach"""
        self.run_module_integration_scenarios(
            ConfigMixIn(
                [],
                ignore_checks=["E0001"],
                include_checks=["I"],
                include_experimental=True,
            )
        )
