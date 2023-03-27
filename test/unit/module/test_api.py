"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from unittest import TestCase

from cfnlint.api import lint, lint_all
from cfnlint.core import get_rules
from cfnlint.helpers import REGIONS
from cfnlint.rules import RulesCollection


class TestLint(TestCase):
    def helper_lint_string_from_file(
        self,
        filename,
        rules=get_rules([], [], ["I", "W", "E"], include_experimental=True),
        regions=REGIONS,
    ):
        with open(filename, "r") as f:
            return lint(f.read(), rules, regions)

    def helper_lint_string_from_file_all(self, filename):
        with open(filename, "r") as f:
            return lint_all(f.read())

    def test_noecho_yaml_template(self):
        filename = "test/fixtures/templates/bad/noecho.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(["W4002", "W4002"], [match.rule.id for match in matches])

    def test_noecho_yaml_template_warnings_ignored(self):
        filename = "test/fixtures/templates/bad/noecho.yaml"
        rules = get_rules([], ["W", "I"], [])
        matches = self.helper_lint_string_from_file(filename, rules=rules)
        self.assertEqual([], matches)

    def test_duplicate_json_template(self):
        filename = "test/fixtures/templates/bad/duplicate.json"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(
            ["E0000", "E0000", "E0000"], [match.rule.id for match in matches]
        )

    def test_invalid_yaml_template(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(["E0000"], [match.rule.id for match in matches])

    def test_invalid_yaml_template_lint_all(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_yaml.yaml"
        matches = self.helper_lint_string_from_file_all(filename)
        self.assertEqual(["E0000"], [match.rule.id for match in matches])

    def test_invalid_json_template(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_json.json"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(["E0000"], [match.rule.id for match in matches])

    def test_invalid_json_template_lint_all(self):
        filename = "test/fixtures/templates/bad/core/config_invalid_json.json"
        matches = self.helper_lint_string_from_file_all(filename)
        self.assertEqual(["E0000"], [match.rule.id for match in matches])

    def test_issues_template(self):
        filename = "test/fixtures/templates/bad/issues.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual(["E1012"], [match.rule.id for match in matches])

    def test_sam_template(self):
        filename = "test/fixtures/templates/good/transform/list_transform_many.yaml"
        matches = self.helper_lint_string_from_file(filename)
        self.assertEqual([], matches)
