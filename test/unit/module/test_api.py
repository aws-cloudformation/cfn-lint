"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import TestCase

from cfnlint import lint, lint_all, lint_by_config, lint_file
from cfnlint.config import ManualArgs
from cfnlint.core import get_rules
from cfnlint.helpers import REGIONS
from cfnlint.rules.errors import ConfigError


class TestLint(TestCase):
    def helper_lint_string_from_file(
        self, filename=None, config: ManualArgs | None = None
    ):
        with open(filename, "r") as f:
            return lint(f.read(), config=config)

    def helper_lint_string_from_file_all(self, filename):
        with open(filename, "r") as f:
            return lint_all(f.read())

    def test_noecho_yaml_template(self):
        filename = "test/fixtures/templates/bad/noecho.yaml"
        matches = self.helper_lint_string_from_file(
            filename=filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["W2010", "W2010"],
            [match.rule.id for match in matches],
            f"Got matches: {matches!r}",
        )

    def test_noecho_yaml_template_warnings_ignored(self):
        filename = "test/fixtures/templates/bad/noecho.yaml"
        matches = self.helper_lint_string_from_file(
            filename=filename,
            config=ManualArgs(
                ignore_checks=["W", "I"],
            ),
        )
        self.assertListEqual([], matches, f"Got matches: {matches!r}")

    def test_duplicate_json_template(self):
        filename = "test/fixtures/templates/bad/duplicate.json"
        matches = self.helper_lint_string_from_file(
            filename=filename,
            config=ManualArgs(
                regions=["us-east-1", "us-west-2", "eu-west-1"],
            ),
        )
        self.assertEqual(
            ["E0000", "E0000", "E0000"],
            [match.rule.id for match in matches],
            f"Got matches: {matches!r}",
        )

    def test_invalid_yaml_template(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"
        matches = self.helper_lint_string_from_file(
            filename=filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["E0000"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_invalid_yaml_template_lint_all(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"
        matches = self.helper_lint_string_from_file_all(filename=filename)
        self.assertEqual(
            ["E0000"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_invalid_json_template(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_json.json"
        matches = self.helper_lint_string_from_file(
            filename=filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["E0000"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_invalid_json_template_lint_all(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_json.json"
        matches = self.helper_lint_string_from_file_all(filename=filename)
        self.assertEqual(["E0000"], [match.rule.id for match in matches])

    def test_issues_template(self):
        filename = "test/fixtures/templates/bad/issues.yaml"
        matches = self.helper_lint_string_from_file(
            filename=filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["E1020"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_sam_template(self):
        filename = "test/fixtures/templates/good/transform/list_transform_many.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual([], matches, f"Got matches: {matches!r}")


class TestV0Usage(TestCase):
    def helper_lint_string_from_file(
        self,
        filename,
        rules=get_rules([], [], ["I", "W", "E"], include_experimental=True),
        regions=REGIONS,
    ):
        with open(filename, "r") as f:
            return lint(f.read(), rules, regions)

    def test_noecho_yaml_template(self):
        filename = "test/fixtures/templates/bad/noecho.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(
            ["W2010", "W2010"],
            [match.rule.id for match in matches],
            f"Got matches: {matches!r}",
        )

    def test_noecho_yaml_template_warnings_ignored(self):
        filename = "test/fixtures/templates/bad/noecho.yaml"
        rules = get_rules([], ["W", "I"], [])
        matches = self.helper_lint_string_from_file(filename, rules=rules)
        self.assertEqual([], matches, f"Got {matches!r}")

    def test_duplicate_json_template(self):
        filename = "test/fixtures/templates/bad/duplicate.json"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(
            ["E0000", "E0000", "E0000"],
            [match.rule.id for match in matches],
            f"Got matches: {matches!r}",
        )

    def test_invalid_yaml_template(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(
            ["E0000"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_invalid_json_template(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_json.json"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(
            ["E0000"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_issues_template(self):
        filename = "test/fixtures/templates/bad/issues.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(
            ["E1020"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_sam_template(self):
        filename = "test/fixtures/templates/good/transform/list_transform_many.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual([], matches, f"Got matches: {matches!r}")


class TestLintFile(TestCase):
    """Test the lint_file API function"""

    def test_nonexistent_file(self):
        """Test linting a file that doesn't exist"""
        matches = lint_file(Path("nonexistent_file.yaml"))
        self.assertEqual(1, len(matches))
        self.assertEqual("E0000", matches[0].rule.id)
        self.assertIn("Template file not found", matches[0].message)

    def test_noecho_yaml_template(self):
        """Test linting a template with NoEcho issues"""
        filename = Path("test/fixtures/templates/bad/noecho.yaml")
        matches = lint_file(
            filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["W2010", "W2010"],
            [match.rule.id for match in matches],
            f"Got matches: {matches!r}",
        )

    def test_noecho_yaml_template_warnings_ignored(self):
        """Test linting with warnings ignored"""
        filename = Path("test/fixtures/templates/bad/noecho.yaml")
        matches = lint_file(
            filename,
            config=ManualArgs(
                ignore_checks=["W", "I"],
            ),
        )
        self.assertListEqual([], matches, f"Got matches: {matches!r}")

    def test_duplicate_json_template(self):
        """Test linting a template with duplicate keys"""
        filename = Path("test/fixtures/templates/bad/duplicate.json")
        matches = lint_file(
            filename,
            config=ManualArgs(
                regions=["us-east-1", "us-west-2", "eu-west-1"],
            ),
        )
        self.assertEqual(
            ["E0000", "E0000", "E0000"],
            [match.rule.id for match in matches],
            f"Got matches: {matches!r}",
        )

    def test_invalid_yaml_template(self):
        """Test linting an invalid YAML template"""
        filename = Path("test/fixtures/templates/bad/core/config_invalid_yaml.yaml")
        matches = lint_file(
            filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["E0000"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_invalid_json_template(self):
        """Test linting an invalid JSON template"""
        filename = Path("test/fixtures/templates/bad/core/config_invalid_json.json")
        matches = lint_file(
            filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["E0000"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_issues_template(self):
        """Test linting a template with issues"""
        filename = Path("test/fixtures/templates/bad/issues.yaml")
        matches = lint_file(
            filename,
            config=ManualArgs(regions=["us-east-1", "us-west-2", "eu-west-1"]),
        )
        self.assertEqual(
            ["E1020"], [match.rule.id for match in matches], f"Got matches: {matches!r}"
        )

    def test_sam_template(self):
        """Test linting a SAM template"""
        filename = Path(
            "test/fixtures/templates/good/transform/list_transform_many.yaml"
        )
        matches = lint_file(filename)
        self.assertEqual([], matches, f"Got matches: {matches!r}")

    def test_empty_file(self):
        """Test linting an empty file"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"")
            temp_file_path = Path(temp_file.name)

        try:
            matches = lint_file(temp_file_path)
            self.assertEqual(1, len(matches))
            self.assertEqual("E1001", matches[0].rule.id)
        finally:
            os.unlink(temp_file_path)

    def test_good_template(self):
        """Test linting a good template"""
        filename = Path("test/fixtures/templates/good/generic.yaml")
        matches = lint_file(filename)
        self.assertEqual([], matches, f"Got matches: {matches!r}")


class TestLintByConfig(TestCase):
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

    def test_lint_by_config_with_valid_config_runs_successfully(self):
        """Test lint_by_config runs successfully with valid config and calls
        runner.run()"""
        # Create a simple valid template file for testing
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  TestResource:
    Type: AWS::S3::Bucket
"""
            )
            temp_file = f.name

        try:
            result = lint_by_config(ManualArgs(templates=[temp_file]))

            # Should return a list (may be empty or contain linting errors,
            # but should not be a config error)
            self.assertIsInstance(result, list)
            # If there are any results, they should not be ConfigError
            for match in result:
                self.assertNotIsInstance(match.rule, ConfigError)

        finally:
            # Clean up the temporary file
            os.unlink(temp_file)
