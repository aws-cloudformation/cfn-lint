"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest

from cfnlint.api import lint_by_config
from cfnlint.config import ManualArgs
from cfnlint.rules.errors import ConfigError


class TestLintByConfig(unittest.TestCase):
    """Test lint_by_config function"""

    def test_lint_by_config_with_invalid_config(self):
        """Test lint_by_config returns ConfigError for invalid configuration"""
        # Test with no templates or deployment files
        result = lint_by_config(ManualArgs())

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0].rule, ConfigError)
        self.assertIn("No templates or deployment files specified", result[0].message)

    def test_lint_by_config_with_conflicting_deployment_files(self):
        """Test lint_by_config returns ConfigError for conflicting deployment files"""
        result = lint_by_config(
            ManualArgs(
                deployment_files=["deployment.yaml"], templates=["template.yaml"]
            )
        )

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0].rule, ConfigError)
        self.assertIn("Deployment files cannot be used with", result[0].message)

    def test_lint_by_config_with_conflicting_parameters(self):
        """Test lint_by_config returns ConfigError for conflicting parameters"""
        result = lint_by_config(
            ManualArgs(
                templates=["template.yaml"],
                parameters={"Key": "Value"},
                parameter_files=["params.json"],
            )
        )

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0].rule, ConfigError)
        self.assertIn(
            "Cannot specify both --parameters and --parameter-files", result[0].message
        )

    def test_lint_by_config_with_multiple_templates_and_parameters(self):
        """Test lint_by_config returns ConfigError for multiple templates
        with parameters
        """
        result = lint_by_config(
            ManualArgs(
                templates=["template1.yaml", "template2.yaml"],
                parameters={"Key": "Value"},
            )
        )

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0].rule, ConfigError)
        self.assertIn(
            "Parameters can only be used with a single template", result[0].message
        )


if __name__ == "__main__":
    unittest.main()
