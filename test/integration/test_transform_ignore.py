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
            "exit_code": 0,
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
