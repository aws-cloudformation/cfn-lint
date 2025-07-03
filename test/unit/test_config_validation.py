"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest

from cfnlint.config import ConfigMixIn, ManualArgs


class TestConfigValidation(unittest.TestCase):
    """Test ConfigMixIn validation functionality"""

    def test_validate_no_templates_or_deployment_files(self):
        """Test validation fails when no templates or deployment files are specified"""
        config = ConfigMixIn(**ManualArgs())

        with self.assertRaises(ValueError) as context:
            config.validate()  # Don't allow stdin for API usage

        self.assertIn(
            "No templates or deployment files specified", str(context.exception)
        )

    def test_validate_no_templates_or_deployment_files_with_stdin_allowed(self):
        """Test validation passes when no templates/deployment files but
        stdin is allowed
        """
        config = ConfigMixIn(**ManualArgs())

        # Should not raise any exception when stdin is allowed
        try:
            config.validate(allow_stdin=True)
        except ValueError:
            self.fail("validate(allow_stdin=True) raised ValueError unexpectedly!")

    def test_validate_deployment_files_with_templates(self):
        """Test validation fails when deployment files are used with templates"""
        config = ConfigMixIn(
            **ManualArgs(
                deployment_files=["deployment.yaml"], templates=["template.yaml"]
            )
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn("Deployment files cannot be used with", str(context.exception))

    def test_validate_deployment_files_with_parameters(self):
        """Test validation fails when deployment files are used with parameters"""
        config = ConfigMixIn(
            **ManualArgs(
                deployment_files=["deployment.yaml"], parameters={"Key": "Value"}
            )
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn("Deployment files cannot be used with", str(context.exception))

    def test_validate_deployment_files_with_parameter_files(self):
        """Test validation fails when deployment files are used with parameter files"""
        config = ConfigMixIn(
            **ManualArgs(
                deployment_files=["deployment.yaml"], parameter_files=["params.json"]
            )
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn("Deployment files cannot be used with", str(context.exception))

    def test_validate_parameters_and_parameter_files(self):
        """Test validation fails when both parameters and parameter
        files are specified
        """
        config = ConfigMixIn(
            **ManualArgs(
                templates=["template.yaml"],
                parameters={"Key": "Value"},
                parameter_files=["params.json"],
            )
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn(
            "Cannot specify both --parameters and --parameter-files",
            str(context.exception),
        )

    def test_validate_multiple_templates_with_parameters(self):
        """Test validation fails when parameters are used with multiple templates"""
        config = ConfigMixIn(
            **ManualArgs(
                templates=["template1.yaml", "template2.yaml"],
                parameters={"Key": "Value"},
            )
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn(
            "Parameters can only be used with a single template", str(context.exception)
        )

    def test_validate_multiple_templates_with_parameter_files(self):
        """Test validation fails when parameter files are used with
        multiple templates
        """
        config = ConfigMixIn(
            **ManualArgs(
                templates=["template1.yaml", "template2.yaml"],
                parameter_files=["params.json"],
            )
        )

        with self.assertRaises(ValueError) as context:
            config.validate()

        self.assertIn(
            "Parameters can only be used with a single template", str(context.exception)
        )

    def test_validate_valid_configuration_with_templates(self):
        """Test validation passes with valid template configuration"""
        config = ConfigMixIn(**ManualArgs(templates=["template.yaml"]))

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_deployment_files(self):
        """Test validation passes with valid deployment files configuration"""
        config = ConfigMixIn(**ManualArgs(deployment_files=["deployment.yaml"]))

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_single_template_and_parameters(self):
        """Test validation passes with single template and parameters"""
        config = ConfigMixIn(
            **ManualArgs(templates=["template.yaml"], parameters={"Key": "Value"})
        )

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_single_template_and_parameter_files(
        self,
    ):
        """Test validation passes with single template and parameter files"""
        config = ConfigMixIn(
            **ManualArgs(templates=["template.yaml"], parameter_files=["params.json"])
        )

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_validate_valid_configuration_with_multiple_templates_no_parameters(self):
        """Test validation passes with multiple templates and no parameters"""
        config = ConfigMixIn(
            **ManualArgs(templates=["template1.yaml", "template2.yaml"])
        )

        # Should not raise any exception
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")


if __name__ == "__main__":
    unittest.main()
